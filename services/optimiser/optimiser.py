import logging

import minizinc
from sqlalchemy import orm
from datetime import datetime

from domain import ShiftRequestVolunteer, UnavailabilityTime
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
        model_str = r"""
        int: R;  % Number of roles
        set of int: ROLE = 1..R;
        
        int: V;  % Number of volunteers
        set of int: VOLUNTEER = 1..V;
        
        int: S;  % Number of shifts
        set of int: SHIFT = 1..S;
        
        % Compatibility matrix (flattened 1D array [S * V] from a 2D matrix)
        array[1..S * V] of bool: compatibility;
        
        % Mastery matrix (flattened 1D array [V * R] from a 2D matrix)
        array[1..V * R] of bool: mastery;
        
        % Skill requirement matrix (flattened 1D array [S * R] from a 2D matrix)
        array[1..S * R] of int: skill_requirements;
        
        % Helper function to map 2D indices to the flattened array
        function int: flat_index_sv(int: s, int: v) = (s - 1) * V + v;
        function int: flat_index_sr(int: s, int: r) = (s - 1) * R + r;
        function int: flat_index_vr(int: v, int: r) = (v - 1) * R + r;
        
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
        
        % A volunteer can only be assigned to a role if they are compatible with the shift
        % AND they have mastery of the role (strict mastery constraint)
        constraint forall(s in SHIFT, v in VOLUNTEER, r in ROLE)(
            possible_assignment[s, v, r] -> (compatibility[flat_index_sv(s, v)] /\ mastery[flat_index_vr(v, r)])
        );
        
        % Soft skill requirement: Encourage, but do not require, filling each role
        var int: unfilled_roles;
        constraint unfilled_roles = sum(s in SHIFT, r in ROLE)(
            bool2int(sum(v in VOLUNTEER)(possible_assignment[s, v, r]) == 0)
        );
        
        % Objective: Maximize assignments and minimize unfilled roles
        solve minimize unfilled_roles + sum(s in SHIFT, v in VOLUNTEER, r in ROLE)(bool2int(possible_assignment[s, v, r]));
        
        % Output the possible assignments per shift
        output ["Possible Assignments:\n"] ++
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
        Save the possible assignments to the database using the repository, checking for conflicts.
        @param result: The model result from MiniZinc
        """
        try:
            assignments = []
            shifts_to_update = set()  # Keep track of shifts to update to PENDING status

            # Process the MiniZinc result by iterating over shifts, volunteers, and roles
            for shift_index, shift_assignments in enumerate(result["possible_assignment"]):  # Iterate over shifts
                shift = self.calculator._shifts_[shift_index]  # Directly access the shift by index

                shifts_to_update.add(shift.id)  # Collect shift IDs to update their status later

                for volunteer_index, volunteer_assignments in enumerate(shift_assignments):  # Iterate over volunteers
                    user = self.calculator.get_volunteer_by_index(volunteer_index)

                    for role_index, is_assigned in enumerate(volunteer_assignments):  # Iterate over roles
                        if is_assigned:  # If a volunteer is assigned to a role for this shift
                            role = self.calculator.get_role_by_index(role_index)

                            # Collect assignment data
                            assignments.append({
                                'user_id': user.id,
                                'shift_id': shift.id,
                                'role_code': role.code,
                                'shift_start': shift.startTime,
                                'shift_end': shift.endTime
                            })

            # Update shifts to PENDING status
            for shift_id in shifts_to_update:
                self.repository.update_shift_pending(shift_id)

            # Use repository method to save all assignments in bulk, conflict checking is done there
            self.repository.save_shift_assignments(assignments)

        except Exception as e:
            logging.error(f"Error processing result data: {e}")
            raise  # Rethrow the exception after logging
