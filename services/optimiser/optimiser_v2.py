import minizinc
from sqlalchemy import orm

from domain import session_scope, AssetRequestVolunteer
from repository.asset_request_volunteer_repository import add_shift
from services.optimiser.calculator import Calculator


class Optimiser:
    calculator = None

    def __init__(self, session: orm.session, request_id: int, debug: bool):
        """
        Initialise the optimiser with session, request_id, and debug mode.
        @param session: The SQLAlchemy session to use.
        @param request_id: The request ID to solve.
        @param debug: If this should be executed in debug (printing) mode.
        """
        self.calculator = Calculator(session, request_id)
        self.debug = debug

    @staticmethod
    def generate_model_string():
        """
        Generate the model string for the optimiser logic.
        This handles volunteer assignment based on shifts (no vehicles).
        @return: A string representation of the MiniZinc model.
        """
        model_str = """
            int: S; % Number of Shifts
            int: V; % Number of Volunteers
            int: P; % Number of Positions
            int: C; % Coefficients for Prioritisation

            set of int: SHIFTS = 1..S;
            set of int: VOLUNTEERS = 1..V;
            set of int: POSITIONS = 1..P;

            array[SHIFTS, POSITIONS] of bool: position_requirements;
            array[VOLUNTEERS, SHIFTS] of bool: availability;
            array[VOLUNTEERS] of bool: personal_transport;

            array[SHIFTS, VOLUNTEERS, POSITIONS] of var bool: assignment;

            constraint forall(s in SHIFTS)(
                sum(p in POSITIONS)(position_requirements[s, p]) >= 
                sum(v in VOLUNTEERS, p in POSITIONS)(bool2int(assignment[s, v, p]))
            );

            constraint forall(s in SHIFTS, v in VOLUNTEERS)(
                sum(p in POSITIONS)(bool2int(assignment[s, v, p])) <= 1
            );

            constraint forall(v in VOLUNTEERS, s in SHIFTS where availability[v, s] == 0)(
                sum(p in POSITIONS)(assignment[s, v, p]) == 0 
            );

            solve maximize (sum(s in SHIFTS, v in VOLUNTEERS, p in POSITIONS)(bool2int(assignment[s, v, p])));

            output ["Assignment: \n"] ++ 
                   [if (show(assignment[s,v,p]) == "true") 
                   then "Shift = " ++ show(s) ++ ", Volunteer = " ++ show(v) ++ ", Position = " ++ show(p) ++ "\n"
                   else "" endif
                   | s in SHIFTS, v in VOLUNTEERS, p in POSITIONS];
        """
        return model_str

    def solve(self):
        """
        Solves the MiniZinc model for the given request using the shift and volunteer data.
        """
        gecode = minizinc.Solver.lookup("coin-bc")
        model = minizinc.Model()
        model.add_string(Optimiser.generate_model_string())
        instance = minizinc.Instance(gecode, model)

        if self.debug:
            print(f"'S' = {self.calculator.get_number_of_shifts()}")
            print(f"'V' = {self.calculator.get_number_of_volunteers()}")
            print(f"'P' = {self.calculator.get_number_of_positions()}")
            print(f"'availability' = {self.calculator.calculate_availability()}")
            print(f"'personal_transport' = {self.calculator.calculate_personal_transport()}")

        # Assigning parameters to the model instance
        instance["S"] = self.calculator.get_number_of_shifts()
        instance["V"] = self.calculator.get_number_of_volunteers()
        instance["P"] = self.calculator.get_number_of_positions()
        instance["availability"] = self.calculator.calculate_availability()
        instance["position_requirements"] = self.calculator.calculate_position_requirements()

        return instance.solve()

    def save_result(self, session, result):
        """
        Save the optimisation result to the database.
        @param session: SQL Alchemy session to use
        @param result: The model result
        """
        # Persist the assignment results
        if result is not None:
            for shift_index, shift in enumerate(result['assignment']):
                for volunteer_index, volunteer in enumerate(shift):
                    for position_index, assigned in enumerate(volunteer):
                        if assigned:
                            role = self.calculator.get_role_by_index(position_index)
                            volunteer = self.calculator.get_volunteer_by_index(volunteer_index)
                            shift = self.calculator.get_shift_by_index(shift_index)
                            print(f'Volunteer {volunteer.email} assigned to position {role.name} for shift {shift.id}')
                            shift_assignment = AssetRequestVolunteer(
                                user_id=volunteer.id,
                                shift_id=shift.id,
                                role_id=role.id,
                                status='pending'
                            )
                            session.add(shift_assignment)
        session.commit()