import sys
from collections import OrderedDict
from operator import itemgetter


content = []

#Opens the text file passed in via sys arguments
for arg in sys.argv[1:]:
    try:
        f = open(arg, 'r')
        for line in f:
            curr_line = line.split()
            # casting from string to integer of time stamps
            curr_line[0] = int(curr_line[0])
            curr_line[1] = int(curr_line[1])
            linedata = curr_line
            content.append(linedata)
    except IOError:
        print'cannot open file'
    except:
        "error in file"
else:
    f.close()

#sorts the data stream according to the node times
content = sorted(content, key=itemgetter(1))


#key-value pair for each potential scenario
confirmation_dict = {
    "HELLO": "ALIVE",
    "LOST" : "DEAD",
    "FOUND": "ALIVE"
}

#ordered dictionary to preserve the order at which the nodes are checked
#node_list is simply updated with the current output message incase the program is stopped at anytime
final_message_dict = OrderedDict()



#this holds the messages for every node for the last 50ms
checker_50ms_dict = OrderedDict()


# this function returns an array in the required printing format
def message_deliverer(notification, message, length, node):
    # timestap from monitor view point
    monitoring_time_stamp = notification[0]

    # justification for nofication such as vader HELLO
    event_detail = notification[2:]

    # output message in required format dependent of length
    if length == 4:
        return [node, "ALIVE", monitoring_time_stamp] + event_detail
    else:
        return [node, message, monitoring_time_stamp] + event_detail


# loop through each line in monitoring system data stream
for current_line in content:
    # retrieve current node time stamp
    current_node_timestamp = current_line[1]

    # as all nodes that output message are automatically alive
    fixed_response = "ALIVE"

    # uses key-value pair for messages
    encoded_message = confirmation_dict[current_line[3]]

    # locate the sending node
    start_node = current_line[2]

    # update output message
    final_message_dict[start_node] = message_deliverer(current_line, encoded_message, 4, start_node)

    # initialise the dict if node does not exist already
    if start_node not in checker_50ms_dict.keys():
        checker_50ms_dict[start_node] = [[], []]

    # reset the dict if the last message was more than 50ms
    elif (current_node_timestamp - checker_50ms_dict[start_node][0][-1]) > 50:
        checker_50ms_dict[start_node] = [[], []]

        # add timestamp and message for the node
    checker_50ms_dict[start_node][0].append(current_node_timestamp)
    checker_50ms_dict[start_node][1].append(fixed_response)

    # check if the node dicovered something
    if len(current_line) == 5:
        # locate node which broadcast is about
        end_node = current_line[4]

        # update output message
        final_message_dict[end_node] = message_deliverer(current_line, encoded_message, 5, end_node)

        # initialise the dict if node does not exist already
        if end_node not in checker_50ms_dict.keys():
            checker_50ms_dict[end_node] = [[], []]

            # reset the dict if the last message was more than 50ms
        elif (current_node_timestamp - checker_50ms_dict[end_node][0][-1]) > 50:
            checker_50ms_dict[end_node] = [[], []]

        # add timestamp and message for the node
        checker_50ms_dict[end_node][0].append(current_node_timestamp)
        checker_50ms_dict[end_node][1].append(encoded_message)

#check if every element in array is the same
#https://stackoverflow.com/questions/3787908/python-determine-if-all-items-of-a-list-are-the-same-item
#all_same function taken from here
def all_same(items):
    return all(x == items[0] for x in items)

#check if all the messages received in the last 50ms are identical
for key,val in checker_50ms_dict.items():
    if (all_same(val[1])!= True):
        final_message_dict[key] = [key, "UNKNOWN", 404,"ERROR"]


#for each element output in required format
for elem in final_message_dict.values():
    elem[2]=str(elem[2])
    print(" ".join(elem))
