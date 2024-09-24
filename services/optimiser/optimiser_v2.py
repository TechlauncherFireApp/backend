import minizinc
from sqlalchemy import orm
from datetime import datetime

from domain import ShiftRequestVolunteer, ShiftRequest
from repository.asset_request_volunteer_repository import add_shift
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

        % Compatibility matrix [VOLUNTEER, ROLE], passed dynamically
        array[VOLUNTEER, ROLE] of bool: compatibility;

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

        % A volunteer can only be assigned to a role if they are compatible with it
        constraint forall(v in VOLUNTEER, r in ROLE)(
            possible_assignment[v, r] -> compatibility[v, r]
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

    def solve(self):
        # Create the MiniZinc model and solver
        gecode = minizinc.Solver.lookup("gecode")
        model = minizinc.Model()
        model.add_string(self.generate_model_string())

        # Create an instance
        instance = minizinc.Instance(gecode, model)

        # Calculate the number of roles and volunteers dynamically
        num_roles = self.calculator.get_number_of_roles()
        num_volunteers = self.calculator.get_number_of_volunteers()

        # Fetch compatibility matrix from the calculator (or create dynamically)
        compatibility_matrix = self.calculator.calculate_compatibility()

        # Assign the dynamic values to the MiniZinc instance
        instance["R"] = num_roles
        instance["V"] = num_volunteers
        instance["compatibility"] = compatibility_matrix

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
