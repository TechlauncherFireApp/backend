import minizinc
from sqlalchemy import orm

from domain import session_scope, ShiftRequestVolunteer
from repository.asset_request_volunteer_repository import add_shift
from services.optimiser.calculator import Calculator


class Optimiser:
    calculator = None

    def __init__(self, session: orm.session, request_id: int, debug: bool = False):
        """
        Initialize the optimiser with session, request_id, and debug mode.
        @param session: The SQLAlchemy session to use.
        @param request_id: The request ID to solve.
        @param debug: If this should be executed in debug (printing) mode.
        """
        self.calculator = Calculator(session, request_id)
        self.debug = debug

    @staticmethod
    def generate_model_string():
        """
        Generate the MiniZinc model string for the optimiser logic.
        This model assigns volunteers to shifts based on availability and other constraints.
        @return: A string representation of the MiniZinc model.
        """
        model_str = """
            int: S; % Number of Shifts
            int: V; % Number of Volunteers
            int: P; % Number of Positions

            set of int: SHIFTS = 1..S;
            set of int: VOLUNTEERS = 1..V;
            set of int: POSITIONS = 1..P;

            array[SHIFTS, POSITIONS] of bool: position_requirements;
            array[VOLUNTEERS, SHIFTS] of bool: availability;
            array[VOLUNTEERS] of bool: personal_transport;

            array[SHIFTS, VOLUNTEERS, POSITIONS] of var bool: assignment;

            % Constraint: Ensure the positions required for each shift are filled.
            constraint forall(s in SHIFTS)(
                sum(p in POSITIONS)(position_requirements[s, p]) >= 
                sum(v in VOLUNTEERS, p in POSITIONS)(bool2int(assignment[s, v, p]))
            );

            % Constraint: Volunteers can be assigned to at most one position per shift.
            constraint forall(s in SHIFTS, v in VOLUNTEERS)(
                sum(p in POSITIONS)(bool2int(assignment[s, v, p])) <= 1
            );

            % Constraint: Volunteers should not be assigned to shifts they are unavailable for.
            constraint forall(v in VOLUNTEERS, s in SHIFTS where availability[v, s] == false)(
                sum(p in POSITIONS)(assignment[s, v, p]) == 0 
            );

            % Objective function: Maximise the number of valid assignments
            solve maximize (
                sum(s in SHIFTS, v in VOLUNTEERS, p in POSITIONS)(
                    bool2int(assignment[s, v, p])
                )
            );

            % Output assignments without using a var in the output condition
            output ["Assignment: \n"] ++ 
                   [if fix(assignment[s,v,p]) == 1 
                    then "Shift = " ++ show(s) ++ ", Volunteer = " ++ show(v) ++ ", Position = " ++ show(p) ++ "\\n"
                    else "" endif
                    | s in SHIFTS, v in VOLUNTEERS, p in POSITIONS];
        """
        return model_str

    def solve(self):
        """
        Solves the MiniZinc model for the given request using the shift and volunteer data.
        """
        gecode = minizinc.Solver.lookup("gecode")
        model = minizinc.Model()
        model.add_string(Optimiser.generate_model_string())
        instance = minizinc.Instance(gecode, model)

        if self.debug:
            print(f"'S' = {self.calculator.get_number_of_shifts()}")
            print(f"'V' = {self.calculator.get_number_of_volunteers()}")
            print(f"'P' = {self.calculator.get_number_of_roles()}")
            print(f"'availability' = {self.calculator.calculate_availability()}")
            print(f"'position_requirements' = {self.calculator.calculate_position_requirements()}")

        # Add model parameters
        instance["S"] = self.calculator.get_number_of_shifts()
        instance["V"] = self.calculator.get_number_of_volunteers()
        instance["P"] = self.calculator.get_number_of_roles()
        instance["availability"] = self.calculator.calculate_availability()
        instance["position_requirements"] = self.calculator.calculate_position_requirements()
        instance["personal_transport"] = self.calculator.calculate_personal_transport()

        result = instance.solve()

        if self.debug:
            print(result)

        return result

    def save_result(self, session, result):
        """
        Save the optimisation result to the database using ShiftRequestVolunteer.
        @param session: SQLAlchemy session to use.
        @param result: The model result from the MiniZinc solver.
        """
        # Iterate through the solution and save it to the database
        if result.solution is not None:
            for shift_index in range(self.calculator.get_number_of_shifts()):
                for volunteer_index in range(self.calculator.get_number_of_volunteers()):
                    for position_index in range(self.calculator.get_number_of_roles()):
                        if result["assignment"][shift_index][volunteer_index][position_index]:
                            shift = self.calculator.get_shift_by_index(shift_index)
                            volunteer = self.calculator.get_volunteer_by_index(volunteer_index)
                            role = self.calculator.get_role_by_index(position_index)

                            print(f'Volunteer {volunteer.email} assigned to position {role.name} for shift {shift.id}')

                            shift_assignment = ShiftRequestVolunteer(
                                user_id=volunteer.id,
                                request_id=shift.id,
                                status='assigned'
                            )
                            session.add(shift_assignment)
        session.commit()
