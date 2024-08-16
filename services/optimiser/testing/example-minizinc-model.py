"""% Number of asset shifts
int: A = 3;
set of int: ASSETSHIFT = 1..A;

% Number of roles
int: R = 2;
set of int: ROLE = 1..R;

% Number of positions
int: P = 2;
set of int: POSITION = 1..P;

% Number of volunteers
int: V = 4;
set of int: VOLUNTEER = 1..V;

% Number of qualifications
int: Q = 2;
set of int: QUALIFICATION = 1..Q;

% Number of coefficients (for prioritization)
int: C = 3;
set of int: COEFFICIENTS = 0..C;

% Supervisor Customization
array[ASSETSHIFT, POSITION, QUALIFICATION] of bool: qualrequirements =
    array3d(ASSETSHIFT, POSITION, QUALIFICATION, [
        % shift 1, position 1
        true, false,  % qualification 1 and 2
        % shift 1, position 2
        false, true,  % qualification 1 and 2
        % shift 2, position 1
        true, true,  % qualification 1 and 2
        % shift 2, position 2
        false, false,  % qualification 1 and 2
        % shift 3, position 1
        true, true,  % qualification 1 and 2
        % shift 3, position 2
        true, false  % qualification 1 and 2
    ]);

array[ASSETSHIFT, POSITION, ROLE] of bool: rolerequirements =
    array3d(ASSETSHIFT, POSITION, ROLE, [
        % shift 1, position 1
        true, false,  % role 1 and 2
        % shift 1, position 2
        false, true,  % role 1 and 2
        % shift 2, position 1
        true, true,  % role 1 and 2
        % shift 2, position 2
        false, false,  % role 1 and 2
        % shift 3, position 1
        true, true,  % role 1 and 2
        % shift 3, position 2
        true, false  % role 1 and 2
    ]);

array[POSITION, ASSETSHIFT] of bool: posrequirements =
    array2d(POSITION, ASSETSHIFT, [
        % position 1
        true, true, true,
        % position 2
        true, true, true
    ]);

% Volunteer Abilities
array[VOLUNTEER, QUALIFICATION] of bool: qualability =
    array2d(VOLUNTEER, QUALIFICATION, [
        % volunteer 1
        true, false,
        % volunteer 2
        true, true,
        % volunteer 3
        true, true,
        % volunteer 4
        true, false
    ]);

array[VOLUNTEER, ROLE] of bool: roleability =
    array2d(VOLUNTEER, ROLE, [
        % volunteer 1
        true, false,
        % volunteer 2
        true, true,
        % volunteer 3
        true, true,
        % volunteer 4
        true, false
    ]);

% Volunteer Availabilities
array[VOLUNTEER, ASSETSHIFT] of bool: availability =
    array2d(VOLUNTEER, ASSETSHIFT, [
        % volunteer 1
        true, true, true,
        % volunteer 2
        true, true, true,
        % volunteer 3
        true, true, true,
        % volunteer 4
        true, true, true
    ]);

array[ASSETSHIFT, ASSETSHIFT] of bool: clashes =
    array2d(ASSETSHIFT, ASSETSHIFT, [
        % shift 1
        true, false, true,
        % shift 2
        false, true, false,
        % shift 3
        true, false, true
    ]);

% Prioritization of Volunteers
array[VOLUNTEER, ASSETSHIFT, ASSETSHIFT] of COEFFICIENTS: shiftcoefficient =
    array3d(VOLUNTEER, ASSETSHIFT, ASSETSHIFT, [
        % volunteer 1
        0, 1, 2, 1, 0, 2, 2, 1, 0,
        % volunteer 2
        1, 0, 2, 0, 1, 2, 2, 0, 1,
        % volunteer 3
        2, 0, 1, 2, 0, 1, 1, 2, 0,
        % volunteer 4
        1, 2, 0, 2, 1, 0, 0, 2, 1
    ]);

% Decision Variable
array[ASSETSHIFT, VOLUNTEER, POSITION] of var bool: assignment;
array[VOLUNTEER, ASSETSHIFT, ASSETSHIFT] of var int: shiftpair;

% % Constraints
% % The number of positions assigned should not exceed the number of positions needed for a shift.
% constraint forall(a in ASSETSHIFT)(
%     sum(p in POSITION)(posrequirements[p, a]) >= sum(p in POSITION, v in VOLUNTEER)(bool2int(assignment[a, v, p]))
% );
% % A volunteer should be assigned to at most one position per shift.
% constraint forall(a in ASSETSHIFT, v in VOLUNTEER)(
%     sum(p in POSITION)(bool2int(assignment[a, v, p])) <= 1
% );
% % A position should only be assigned to at most once for all shifts.
% constraint forall(p in POSITION)(
%     sum(a in ASSETSHIFT, v in VOLUNTEER)(assignment[a, v, p]) <= 1
% );
% % If a volunteer either does not have the qualification or role for a position, then they should not be assigned to a shift.
% constraint forall(a in ASSETSHIFT, p in POSITION, v in VOLUNTEER, r in ROLE, q in QUALIFICATION where ((qualrequirements[a, p, q] == true /\ qualability[v, q] == false) \/ (rolerequirements[a, p, r] == true /\ roleability[v, r] == false)))(
%     bool2int(assignment[a, v, p]) == 0
% );
% % If a volunteer is not available for a shift, they should not be assigned in the shift.
% constraint forall(v in VOLUNTEER, a in ASSETSHIFT where availability[v, a] == 0)(
%     sum(p in POSITION)(assignment[a, v, p]) == 0
% );
% % If a shift clashes with another shift, then the volunteer should not be assigned to both shifts.
% constraint forall(aone in ASSETSHIFT, v in VOLUNTEER)(
%     forall(atwo in ASSETSHIFT where clashes[aone, atwo] == true)(
%         not(sum(p in POSITION)(assignment[aone, v, p]) == true /\ sum(p in POSITION)(assignment[atwo, v, p]) == true)
%     )
% );
% % Volunteers should only be assigned to a position that is needed for the shift. i.e. there should not be any positions assigned for a shift if it hasn't been
% % intended by the supervisor through customisation.
% constraint forall(a in ASSETSHIFT, v in VOLUNTEER, p in POSITION)(
%     not(assignment[a, v, p] == true /\ posrequirements[p, a] == false)
% );

% Objective
solve maximize sum(a in ASSETSHIFT, v in VOLUNTEER, p in POSITION)(bool2int(assignment[a,v,p]));

% Debugging statement
output [ "Debug: Check Assignments\n"] ++
       [
           "Total assignments made: " ++ show(sum([bool2int(fix(assignment[a, v, p])) | a in ASSETSHIFT, v in VOLUNTEER, p in POSITION])) ++ "\n"
       ];

% OUTPUT
output [ "Assignment: \n"] ++
       [
           "Asset Shift = " ++ show(a) ++ "\n" ++
           concat([
               if fix(assignment[a, v, p]) == true then
                  "  Volunteer = " ++ show(v) ++ ",  Position = " ++ show(p) ++ "\n"
               else ""
               endif
               | v in VOLUNTEER, p in POSITION
           ])
           | a in ASSETSHIFT
       ];
"""