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
        int: A = 3;
        set of int: ASSETSHIFT = 1..A;

        int: R = 2;
        set of int: ROLE = 1..R;

        int: P = 2;
        set of int: POSITION = 1..P;

        int: V = 4;
        set of int: VOLUNTEER = 1..V;

        int: Q = 2;
        set of int: QUALIFICATION = 1..Q;

        % Decision Variable
        array[ASSETSHIFT, VOLUNTEER, POSITION] of var bool: assignment;

        % Constraints
        constraint forall(a in ASSETSHIFT)(
            sum(p in POSITION)(sum(v in VOLUNTEER)(bool2int(assignment[a, v, p]))) <= R
        );

        solve satisfy;

        % OUTPUT
        output [
            "Assignments: \\n"
        ] ++ [
            "Asset Shift ", show(a), ": ",
            concat([if fix(assignment[a, v, p]) then
                    "Volunteer ", show(v), " assigned to Position ", show(p), "\\n"
                    else ""
                    endif | v in VOLUNTEER, p in POSITION])
            | a in ASSETSHIFT
        ];
        """
        return model_str

    def solve(self):
        # Create a MiniZinc model and instance
        gecode = minizinc.Solver.lookup("coin-bc")
        model = minizinc.Model()
        model.add_string(self.generate_model_string())

        # Create the instance
        instance = minizinc.Instance(gecode, model)

        # Example: Add your custom logic for parameters here (e.g., qualifications, roles, availability)
        # Example:
        # instance["A"] = self.calculator.get_number_of_shifts()
        # instance["R"] = self.calculator.get_number_of_roles()
        # instance["V"] = self.calculator.get_number_of_volunteers()

        result = instance.solve()

        if self.debug:
            print(result)

        return result


    def save_result(self, session, result) -> None:
        """
        Save a model result to the database.
        @param session: SQL Alchemy session to use
        @param result: The model result
        """
        # Simple data structure to help find whats missing and whats populated from the decision variable
        persist = []
        for x in self.calculator.get_asset_requests():
            roles = {}
            for role in self.calculator.get_roles():
                roles[role.id] = {'count': self.calculator.get_role_count(x.asset_type.id, role.id), 'assigned': []}
            persist.append(roles)

        # Iterate over the results, adding them to our persistence data structure
        if result is not None:
            for asset_request_index, asset_request in enumerate(result['contrib']):
                for volunteer_index, volunteer in enumerate(asset_request):
                    for role_index, assigned in enumerate(volunteer):
                        if assigned:
                            role_domain = self.calculator.get_role_by_index(role_index)
                            user_domain = self.calculator.get_volunteer_by_index(volunteer_index)
                            asset_request_domain = self.calculator.get_asset_request_by_index(asset_request_index)
                            print(
                                f'Volunteer {user_domain.email} should be assigned to role {role_domain.code} on asset request {asset_request_domain.id}')
                            asset_request_obj = persist[asset_request_index]
                            role_map = asset_request_obj[role_domain.id]
                            role_map['assigned'].append(user_domain.id)

        # Now, actually persist it!
        for asset_request_index, _ in enumerate(persist):
            asset_request = self.calculator.get_asset_request_by_index(asset_request_index)
            asset_request_roles = persist[asset_request_index]
            for role_id in asset_request_roles:
                for assign_count in range(asset_request_roles[role_id]['count']):
                    if assign_count < len(asset_request_roles[role_id]['assigned']):
                        ar = AssetRequestVolunteer(user_id=asset_request_roles[role_id]['assigned'][assign_count],
                                                   vehicle_id=asset_request.id, role_id=role_id, status='pending')
                    else:
                        ar = AssetRequestVolunteer(user_id=None, vehicle_id=asset_request.id, role_id=role_id)
                    session.add(ar)
