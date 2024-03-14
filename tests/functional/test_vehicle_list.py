from services.optimiser.input_processing import get_vehicle_list, get_position_list

# This can be called by api from postman, to tests easily
def test_vehicle_list(session, request_id):
   v_l = get_vehicle_list(session, request_id)
   for v in v_l:
      get_position_list(session, v)

    # print("get_postion_role", get_position_role(session,720))
    # print("get_APR_matrix", get_input_rolerequirements(session,361))
    # get_position_qualification(session,756)
    # print("get_APQ_matrix",get_input_qualrequirements(session,361))
    # print("get_position_list_all",get_position_list_all(session,360))
    # print("get_position_vehicle",get_position_vehicle(session,863))
    # print("get_posrequirements_matrix",get_input_posrequirements(session,360))
    # get_input_qualability(session)
    # print(get_qualification_list(session))
    # print(get_input_qualability(session))
    # get_role_list(session)
    # print(get_input_roleability(session))
    # print(get_vehicle_time(session,369))
    # print(get_input_availability(session,360))
    # print(time_unavailability_list(session,31))
    # print(get_input_availability(session,360))
    # print(get_input_clashes(session,323))


   return 1