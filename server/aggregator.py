# // One of the clients has sent us a message.
# // Right now we can only receive "new_weights" types of messages.
#
# // 1. If the round in the received message doesn't match the internal round,
# //    then discard the message.
#
# // 2 Lock section/variables that will be changed...
#
# // 2. If 'Continuation Criteria' isn't met...
#
#     // 2.a. Do running weighted average on the new weights.
#
#     // 2.b. Update the number of nodes averaged (+1)
#
# // 3. If 'Continuation Criteria' is met...
#
#     // 3.a. Update the number of nodes averaged (+1)
#
#     // 3.b. Log the resulting weights for the user (for this round)
#
#     // 3.c. Update round number (+1)
#
#     // 3.d. If 'Termination Criteria' isn't met, then kickstart a new FL round
#     //      NOTE: We need a way to swap the weights from the initial message
#     //      in node............
#
# // 4. If 'Termination Criteria' is met...
#
#     // 4.a. Log the resulting weights for the user (for this session)
#
#     // 4.b. Reset all state in the service and mark BUSY as false
#
# // 5. Release section/variables that were changed...


# // NOTE: We need to implement some ping-pong/ways to deal with disconnections.
