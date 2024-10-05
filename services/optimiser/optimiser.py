import logging
import minizinc
from sqlalchemy import orm
from datetime import datetime

from domain import ShiftRequestVolunteer
from services.optimiser.calculator import Calculator
from repository.shift_repository import ShiftRepository

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Optimiser:
    # The calculator generates data structures for the optimiser to solve.
    calculator = None

    def __init__(self, session: orm.session, repository: ShiftRepository, debug: bool):
        """
        @param session: The SQLAlchemy session to use
        @param repository: The repository class for database operations.
        @param debug: If this should be executed in debug (printing) mode.
        """
        self.calculator = Calculator(session)
        self.repository = repository
        self.debug = debug

    @staticmethod
    def generate_model_string():
        """
        Generate the MiniZinc model string for the optimiser.
        @return: The MiniZinc model as a string.
        """
        model_str = """
        int: R;  % Number of roles
        set of int: ROLE = 1..R;

        int: V;  % Number of volunteers
        set of int: VOLUNTEER = 1..V;

        int: S;  % Number of shifts
        set of int: SHIFT = 1..S;

        % Compatibility matrix (flattened 1D array [V * R] from a 2D matrix)
        array[1..V * R] of bool: compatibility;

        % Mastery matrix (flattened 1D array [V * R] from a 2D matrix)
        array[1..V * R] of bool: mastery;

        % Skill requirement matrix (flattened 1D array [S * R] from a 2D matrix)
        array[1..S * R] of int: skill_requirements;

        % Helper function to map 2D indices to the flattened array
        function int: flat_index(int: s, int: r) = (s - 1) * R + r;

        % Decision variable: assignment of volunteers to roles for each shift
        array[SHIFT, VOLUNTEER, ROLE] of var bool: possible_assignment;

        % Constraints
        % A volunteer should be assigned to at most one role per shift
        constraint forall(s in SHIFT, v in VOLUNTEER)(
            sum(r in ROLE)(bool2int(possible_assignment[s, v, r])) <= 1
        );

        % A role should only be assigned to at most one volunteer per shift
        constraint forall(s in SHIFT, r in ROLE)(
            sum(v in VOLUNTEER)(bool2int(possible_assignment[s, v, r])) <= 1
        );

        % A volunteer can only be assigned to a role if they are compatible with it and have mastery of the role
        constraint forall(s in SHIFT, v in VOLUNTEER, r in ROLE)(
            possible_assignment[s, v, r] -> (compatibility[flat_index(v, r)] /\ mastery[flat_index(v, r)])
        );

        % Ensure that each role meets the required skill for the shift
        constraint forall(s in SHIFT, r in ROLE)(
            sum(v in VOLUNTEER)(bool2int(possible_assignment[s, v, r])) >= skill_requirements[flat_index(s, r)]
        );

        % Objective: Maximize the number of valid role assignments
        solve maximize sum(s in SHIFT, v in VOLUNTEER, r in ROLE)(bool2int(possible_assignment[s, v, r]));

        % Output the possible assignments per shift
        output ["Possible Assignments:\\n"] ++
               [ "Shift = " ++ show(s) ++ ", Volunteer = " ++ show(v) ++ ", Role = " ++ show(r) ++ "\n"
                 | s in SHIFT, v in VOLUNTEER, r in ROLE where fix(possible_assignment[s, v, r])
               ];
        """
        return model_str

    @staticmethod
    def flatten_compatibility(compatibility_2d):
        """
        Flattens a 2D compatibility matrix into a 1D list for MiniZinc.

        :param compatibility_2d: A 2D list where each row represents a volunteer's compatibility with roles
        :return: A 1D list representing the flattened compatibility matrix
        """
        return [item for sublist in compatibility_2d for item in sublist]

    @staticmethod
    def flatten_skill_requirements(skill_requirements_2d):
        """
        Flattens a 2D skill requirement matrix into a 1D list for MiniZinc.

        :param skill_requirements_2d: A 2D list where each row represents skill requirements per shift and role
        :return: A 1D list representing the flattened skill requirements matrix
        """
        return [item for sublist in skill_requirements_2d for item in sublist]

    def solve(self):
        logger.info("Starting the solve process.")

        # Create the MiniZinc model and solver
        gecode = minizinc.Solver.lookup("gecode")
        model = minizinc.Model()
        model.add_string(self.generate_model_string())



        # Calculate the number of roles, volunteers, and shifts dynamically
        num_roles = self.calculator.get_number_of_roles()
        num_positions = self.calculator.get_shift_position_count()
        num_volunteers = self.calculator.get_number_of_volunteers()
        num_shifts = self.calculator.get_shift_count()

        logger.info(f"Number of roles: {num_roles}, Number of volunteers: {num_volunteers}, Number of shifts: {num_shifts}")

        # Fetch compatibility matrix from the calculator
        compatibility_2d = self.calculator.calculate_compatibility()
        logger.info(f"Compatibility matrix (2D): {compatibility_2d}")

        # Fetch mastery matrix from the calculator
        mastery_2d = self.calculator.calculate_mastery()
        logger.info(f"Mastery matrix (2D): {mastery_2d}")

        # Fetch skill requirements matrix from the calculator
        skill_requirements_2d = self.calculator.calculate_skill_requirement()
        logger.info(f"Skill requirements matrix (2D): {skill_requirements_2d}")

        # Flatten the 2D compatibility, mastery, and skill requirements matrices
        flattened_compatibility = self.flatten_compatibility(compatibility_2d)
        flattened_mastery = self.flatten_compatibility(mastery_2d)
        flattened_skill_requirements = self.flatten_skill_requirements(skill_requirements_2d)

        logger.info(f"Flattened compatibility: {flattened_compatibility}")
        logger.info(f"Flattened mastery: {flattened_mastery}")
        logger.info(f"Flattened skill requirements: {flattened_skill_requirements}")

        # Create an instance
        instance = minizinc.Instance(gecode, model)

        # Assign the dynamic values to the MiniZinc instance
        instance["R"] = num_roles
        instance["V"] = num_volunteers
        instance["S"] = num_shifts
        instance["compatibility"] = flattened_compatibility
        instance["mastery"] = flattened_mastery
        instance["skill_requirements"] = flattened_skill_requirements

        logger.info("Starting to solve the MiniZinc instance.")
        # Solve the instance
        result = instance.solve()

        if self.debug:
            print(result)

        logger.info("Solve process completed.")
        return result

    def save_result(self, result) -> None:
        """
        Save the possible assignments to the ShiftRequestVolunteer table with status PENDING.
        @param result: The model result from MiniZinc
        """
        shift_volunteers = []

        try:
            # Process the MiniZinc result by iterating over shifts, roles, and volunteers
            for shift_index, shift_assignments in enumerate(result["possible_assignment"]):  # Iterate over shifts
                shift = self.calculator._shifts_[shift_index]  # Directly access the shift by index
                for role_index, role_assignments in enumerate(shift_assignments):  # Iterate over roles in the shift
                    for volunteer_index, is_assigned in enumerate(role_assignments):  # Iterate over volunteers
                        if is_assigned:  # If a volunteer is assigned to a role for this shift
                            user = self.calculator.get_volunteer_by_index(volunteer_index)
                            role = self.calculator.get_role_by_index(role_index)

                            # Create a ShiftRequestVolunteer entry with status PENDING
                            shift_volunteer = ShiftRequestVolunteer(
                                user_id=user.id,
                                # request_id in ShiftRequestVolunteer is the actual shift id itself
                                request_id=shift.id,
                                position_id=role.id,
                                # Marking as ACCEPTED because frontend does not have a function to
                                # change PENDING to ACCEPTED (not in SOW)
                                status='ACCEPTED',
                                update_date_time=datetime.now(),
                                insert_date_time=datetime.now(),
                            )
                            shift_volunteers.append(shift_volunteer)

            # Commit the results to the database
            self.repository.save_shift_volunteers(shift_volunteers)

        except Exception as e:
            logging.error(f"Error processing result data: {e}")
            raise  # Rethrow the exception after logging
