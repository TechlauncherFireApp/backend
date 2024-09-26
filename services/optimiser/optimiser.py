import minizinc
from sqlalchemy import orm
from datetime import datetime

from domain import ShiftRequestVolunteer
from services.optimiser.calculator import Calculator


class Optimiser:
    # The calculator generates data structures for the optimiser to solve.
    calculator = None

    def __init__(self, session: orm.session, request_id: int, debug: bool):
        """
        @param session: The SQLAlchemy session to use.
        @param request_id: The ShiftRequest ID to solve.
        @param debug: If this should be executed in debug (printing) mode.
        """
        self.calculator = Calculator(session, request_id)
        self.debug = debug

    @staticmethod
    def generate_model_string():
        """
        Generate the MiniZinc model string for the optimiser.
        @return: The MiniZinc model as a string.
        """
        model_str = """
        int: R;  % Number of roles, passed dynamically
        set of int: ROLE = 1..R;

        int: V;  % Number of volunteers, passed dynamically
        set of int: VOLUNTEER = 1..V;

        int: S;  % Number of shifts, passed dynamically
        set of int: SHIFT = 1..S;

        % Compatibility matrix passed as a flat array [V * R]
        array[1..V * R] of bool: compatibility;

        % Mastery matrix passed as a flat array [V * R]
        array[1..V * R] of bool: mastery;

        % Skill requirement matrix passed as a 2D array [SHIFT, ROLE]
        array[SHIFT, ROLE] of int: skill_requirements;

        % Helper function to map 2D indices to the flattened array
        function int: flat_index(int: v, int: r) = (v - 1) * R + r;

        % Decision variable: assignment of volunteers to roles
        array[VOLUNTEER, ROLE] of var bool: possible_assignment;

        % Constraints
        % A volunteer should be assigned to at most one role
        constraint forall(v in VOLUNTEER)(
            sum(r in ROLE)(bool2int(possible_assignment[v, r])) <= 1
        );

        % A role should only be assigned to at most one volunteer
        constraint forall(r in ROLE)(
            sum(v in VOLUNTEER)(bool2int(possible_assignment[v, r])) <= 1
        );

        % A volunteer can only be assigned to a role if they are compatible with it and have mastery of the role
        constraint forall(v in VOLUNTEER, r in ROLE)(
            possible_assignment[v, r] -> (compatibility[flat_index(v, r)] /\ mastery[flat_index(v, r)])
        );

        % Ensure that each role meets the required skill for the shift
        constraint forall(s in SHIFT, r in ROLE)(
            sum(v in VOLUNTEER)(bool2int(possible_assignment[v, r])) >= skill_requirements[s, r]
        );

        % Objective: Maximize the number of valid role assignments
        solve maximize sum(v in VOLUNTEER, r in ROLE)(bool2int(possible_assignment[v, r]));

        % Output the possible assignments
        output ["Possible Assignments:\\n"] ++
               [ if fix(possible_assignment[v, r]) then
                   "Volunteer = " ++ show(v) ++ ", Role = " ++ show(r) ++ "\\n"
                 else ""
                 endif
                 | v in VOLUNTEER, r in ROLE
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

    def solve(self):
        # Create the MiniZinc model and solver
        gecode = minizinc.Solver.lookup("gecode")
        model = minizinc.Model()
        model.add_string(self.generate_model_string())

        # Create an instance
        instance = minizinc.Instance(gecode, model)

        # Calculate the number of roles, volunteers, and shifts dynamically
        num_roles = self.calculator.get_number_of_roles()
        num_volunteers = self.calculator.get_number_of_volunteers()
        num_shifts = len(self.calculator._shifts_)

        # Fetch compatibility matrix from the calculator
        compatibility_2d = self.calculator.calculate_compatibility()

        # Fetch mastery matrix from the calculator
        mastery_2d = self.calculator.calculate_mastery()

        # Fetch skill requirements matrix from the calculator
        skill_requirements = self.calculator.calculate_skill_requirement()

        # Flatten the 2D compatibility and mastery matrices
        flattened_compatibility = self.flatten_compatibility(compatibility_2d)
        flattened_mastery = self.flatten_compatibility(mastery_2d)

        # Assign the dynamic values to the MiniZinc instance
        instance["R"] = num_roles
        instance["V"] = num_volunteers
        instance["S"] = num_shifts
        instance["compatibility"] = flattened_compatibility
        instance["mastery"] = flattened_mastery
        instance["skill_requirements"] = skill_requirements

        # Solve the instance
        result = instance.solve()

        if self.debug:
            print(result)

        return result

    def save_result(self, session, result) -> None:
        """
        Save the possible assignments to the ShiftRequestVolunteer table with status PENDING.
        @param session: SQLAlchemy session to use
        @param result: The model result from MiniZinc
        """
        shift_request_id = self.calculator.request_id

        # Process the MiniZinc result
        for role_index, role_assignments in enumerate(result["possible_assignment"]):
            for volunteer_index, is_assigned in enumerate(role_assignments):
                if is_assigned:  # If a volunteer is assigned to a role
                    user = self.calculator.get_volunteer_by_index(volunteer_index)
                    role = self.calculator.get_role_by_index(role_index)

                    # Create a ShiftRequestVolunteer entry with status PENDING
                    shift_volunteer = ShiftRequestVolunteer(
                        user_id=user.id,
                        request_id=shift_request_id,
                        position_id=role.id,
                        status='PENDING',  # Marking as pending since it's just a possible assignment
                        update_date_time=datetime.now(),
                        insert_date_time=datetime.now(),
                    )
                    session.add(shift_volunteer)

        # Commit the results to the database
        session.commit()
