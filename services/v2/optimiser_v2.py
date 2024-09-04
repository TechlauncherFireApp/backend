import minizinc
from sqlalchemy import orm

from domain import session_scope, AssetRequestVolunteer
from repository.asset_request_volunteer_repository import add_shift
from services.optimiser.calculator import Calculator


class Optimiser:
    # The calculator generates data structures for the optimiser to solve.
    calculator = None

    def __init__(self, session: orm.session, request_id: int, debug: bool):
        """
        @param session: The SQLAlchemy session to use.
        @param request_id: The request ID to solve.
        @param debug: If this should be executed in debug (printing) mode.
        """
        self.calculator = Calculator(session, request_id)
        self.debug = debug

    @staticmethod
    def generate_model_string():
        """
        Generate the MiniZinc model string for the optimiser.
        @return:
        """
        model_str = """
        int: V;  % Number of volunteers, passed dynamically
        set of int: VOLUNTEER = 1..V;
        
        int: S;  % Number of shifts, passed dynamically
        set of int: SHIFT = 1..S;
        
        int: R;  % Number of roles, passed dynamically
        set of int: ROLE = 1..R;
        
        % Compatibility matrix [VOLUNTEER, SHIFT], passed dynamically
        array[VOLUNTEER, SHIFT] of bool: compatibility;
        
        % Decision variable: assignment of volunteers to roles in shifts
        array[VOLUNTEER, SHIFT, ROLE] of var bool: assignment;
        
        % Constraints
        % A volunteer should be assigned to at most one role per shift.
        constraint forall(v in VOLUNTEER, s in SHIFT)(
            sum(r in ROLE)(bool2int(assignment[v, s, r])) <= 1
        );
        
        % A role should only be assigned to at most one volunteer per shift.
        constraint forall(s in SHIFT, r in ROLE)(
            sum(v in VOLUNTEER)(bool2int(assignment[v, s, r])) <= 1
        );
        
        % A volunteer can only be assigned to a role in a shift if they are compatible with the shift.
        constraint forall(v in VOLUNTEER, s in SHIFT)(
            sum(r in ROLE)(bool2int(assignment[v, s, r])) <= bool2int(compatibility[v, s])
        );
        
        % Objective: Maximize the number of valid role assignments
        solve maximize sum(v in VOLUNTEER, s in SHIFT, r in ROLE)(bool2int(assignment[v, s, r]));
        
        % Output the assignments
        output ["Assignments:\n"] ++
               [ if fix(assignment[v, s, r]) then
                   "Volunteer = " ++ show(v) ++ ", Shift = " ++ show(s) ++ ", Role = " ++ show(r) ++ "\n"
                 else ""
                 endif
                 | v in VOLUNTEER, s in SHIFT, r in ROLE
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

        # Assuming shifts are defined by the shift blocks in the compatibility calculation
        num_shifts = len(self.calculator.calculate_compatibility()[0])  # Number of shift blocks

        # Fetch compatibility matrix from the calculator (or create dynamically)
        compatibility_matrix = self.calculator.calculate_compatibility()

        # Assign the dynamic values to the MiniZinc instance
        instance["R"] = num_roles
        instance["V"] = num_volunteers
        instance["S"] = num_shifts
        instance["compatibility"] = compatibility_matrix

        # Solve the instance
        result = instance.solve()

        if self.debug:
            print(result)

        return result

    def save_result(self, session, result) -> None:
        """
        Save a model result to the database.
        @param session: SQLAlchemy session to use
        @param result: The model result
        """
        for asset_request_index, asset_request in enumerate(result["assignment"]):
            for volunteer_index, volunteer in enumerate(asset_request):
                for position_index, assigned in enumerate(volunteer):
                    if assigned:
                        # Here, save assignments to the database
                        pass
