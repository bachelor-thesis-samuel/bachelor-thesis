import sys
from random import randint, random
from numpy import prod, log, random, power

"""
This program creates an instance of a binary fair division problem.
Then it solves the instance for an optimal solution based on the ALG-BINARY algorithm
proposed in "Greedy Algorithms for Maximizing Nash Social Welfare" by
Siddharth Barman, Sanath Kumar Krishnamurthy and Rohit Vaish.
"""

# ##### GLOBALS ######

agent_quantity = 7          # number of agents that we will use
item_quantity = 16          # number of items that will be created
liking_probability = 0.5    # probability that an agent likes a given item

# ##### Functions ######

def coinflip(liking_probability):
    """
    This function flips a biased coin based on the liking_probability parameter.
    With the given probability, it returns True and False otherwise.
    Used for filling the agents' personal preferences.
    """

    if random.random() < liking_probability:
        agent_liking = True
    else:
        agent_liking = False

    return agent_liking


def create_agents(agent_quantity):
    """
    This function creates agents via a list that contains agent-many sub-lists.
    These sub-lists correspond to a specific agent. For now, they will be emtpy.
    Later (see create_agent_preferences), they will contain every agent's preference towards every item.
    """

    agent_list = []                             # this list will contain agent-many empty lists

    for agent in range(0, agent_quantity):      # for each agent
        agent_list.append([])                   # appending an empty list to be filled

    return agent_list


def create_agent_preferences(agent_list):
    """
    This function creates the individual likings of our agents.
    It does so, by filling up the list of agents with individual likings.
    It creates item-many boolean entries for each agent.
    As we need all items to be distributable, the last agent will like all items.
    This ensures that we only have solvable instances. However, this might cause this last agent to be unreachable.
    This is because with low (liking_probability), there might be uniformly disliked items,
    which the last agent receives per definition.
    """

    for agent in range(0, agent_quantity):          # every agent gets preferences

        specific_preferences = []                   # this agent's preferences are empty and to be filled randomly

        for item in range(0, item_quantity):        # for every item we get a boolean liking

            liking = coinflip(liking_probability)   # evaluation of an item is 0 or 1, hence a random bit
            specific_preferences.append(liking)     # the preferences for this agent are collected

        agent_list[agent] = specific_preferences    # we save this agent's preferences to the total list

    agent_list[agent_quantity - 1] = [True] * item_quantity  # this creates an agent who likes all items at the end

    return agent_list


def random_allocation(preferences):
    """
    This function creates a random non-wasteful allocation.
    It creates a list of length item_quantity that "maps" every item to an agent.

    First, each agent is given an item that they like.
    This is done by a loop over the agents and then an iteration over the possible items. A manual check ensures,
    that each item given is also liked. After distributing an item to an agent, the next agent is up.
    Thus, every agent receives exactly one item in this part of the allocaiton.
    We also mark all distributed items to the agents so they will not be taken away in the second stage.

    In the second stage, we give all the items, that have not been distributed yet (m-n) to agents randomly.
    To do this, we create a list called "leftover_items", that marks which items have been distributed.
    Then we iterate only over the undistributed items.
    To remain non-wasteful, we check for every item whether their owner likes it or not.
    """

    leftover_items = [0] * item_quantity    # contains distributed items to protect them from being re-distributed
    allocation = ["x"] * item_quantity      # contains our allocation

    #
    # This is the first part of the item allocation.
    #

    for agent in range(0, agent_quantity):      # we will provide each agent with an item
        for item in range(0, item_quantity):    # we check their preferences until we find a "True" value

            if preferences[agent][item] and leftover_items[item] != 1:  # if we've found a liked, undistributed item
                allocation[item] = agent                                # allocates the item to the agent
                leftover_items[item] = 1                                # mark allocated item
                break                                                   # continue with the next agent

    #
    # Here, the second part of the allocation is done.
    #

    for leftover_item in range(0, len(leftover_items)):             # check undistributed items

        if leftover_items[leftover_item] != 1:                      # if this item has not been distributed yet
            infinity_counter = 0                        # we need to keep track if too few agents like this item

            while True:                                             # try to allocate item to random agent

                if infinity_counter > agent_quantity ** 2:          # check if we've tried allocating an item for long
                    allocation[leftover_item] = agent_quantity - 1  # allocate it to the last agent
                    break

                x = randint(0, agent_quantity - 2)                  # choose random agent
                infinity_counter = infinity_counter + 1             # increment the tries

                if preferences[x][leftover_item]:                   # if the agent likes the item: allocate it
                    allocation[leftover_item] = x
                    break

                else:                                               # if they don't: try another agent
                    pass

    return allocation


def stupid_allocation(preferences):
    """
    This function creates a random non-wasteful but LESS EVENLY DISTRIBUTED allocation.
    It works exactly like the random allocation but picks the random agents from a small sample.
    """

    leftover_items = [0] * item_quantity        # contains distributed items to protect them from being re-distributed
    allocation = ["x"] * item_quantity          # contains our allocation

    #
    # This is the first part of the item allocation.
    #

    for agent in range(0, agent_quantity):      # we will provide each agent with an item
        for item in range(0, item_quantity):    # we check their preferences until we find a "True" value

            if preferences[agent][item] and leftover_items[item] != 1:  # if we've found a liked, undistributed item
                allocation[item] = agent        # allocates the item to the agent
                leftover_items[item] = 1        # mark allocated item
                break                           # continue with the next agent

    #
    # Here, the second part of the allocation is done.
    #

    for leftover_item in range(0, len(leftover_items)):     # check undistributed items

        if leftover_items[leftover_item] != 1:              # if this item has not been distributed yet
            infinity_counter = 0                            # we need to keep track if too few agents like this item

            while True:                                     # try to allocate item to random agent

                if infinity_counter > agent_quantity ** 2:  # check if we've tried allocating an item for long
                    allocation[leftover_item] = agent_quantity - 1  # allocate it to the last agent
                    break

                x = randint(0, round(agent_quantity / 5))   # choose random agent
                print(x)
                infinity_counter = infinity_counter + 1     # increment the tries

                if preferences[x][leftover_item]:           # if the agent likes the item: allocate it
                    allocation[leftover_item] = x
                    break

                else:                                       # if they don't: try another agent
                    pass

    return allocation



def split_nsw(agent_values):
    """
    This function computes the NSW of a given problem instance.
    It computes the formula based on an array of agents' utility ratings.
    It also splits the multiplication into small chunks to make them computable.
    """

    counter = 0
    product = 1                                         # we differentiate between 2 products
    rooted_product = 1                                  # one contains normal products, the is already rooted

    for value in agent_values:

        counter = counter + 1
        product = product * value                       # calculate product with this value

        if counter % 20 == 0:                           # we append the product to the rooted product step by step

            product = product ** (1 / agent_quantity)   # root the product of the last twenty values
            rooted_product = rooted_product * product   # calculate the new rooted product
            product = 1                                 # reset the product

        else:
            pass

    product = product ** (1 / agent_quantity)
    final_product = rooted_product * product

    return final_product


def nash_social_welfare(agent_values):
    """
    This function computes the NSW of a given problem instance.
    It computes the formula based on an array of agents' utility ratings.
    """

    if prod(agent_values) < 0:
        print("Die Eingabegröße ist zu groß!")                      # catches numpy/python struggling

    nsw_value = power(prod(agent_values), abs(1 / agent_quantity))  # compute the nsw of the allocation

    return nsw_value


def calculate_agent_valuations(allocation):
    """
    This function finds the utility values of each agent.
    It returns an array with these valuations.
    """

    agent_values = [0] * agent_quantity         # will store each agents' baskets valuation, contains zeros for now

    for item in range(0, item_quantity):        # every item becomes evaluated

        agent_values[allocation[item]] += 1     # increase this agent's welfare by 1

    return agent_values


def fast_nsw(path, allocation):
    """
    This function takes a path given as a list by the APSP solution
    and computes the nsw as if we were to reallocate the items along that path.
    """

    agent_values = calculate_agent_valuations(allocation)                       # count agents valuations

    agent_values[path[0]] = agent_values[path[0]] + 1                           # increase the value of the receiver
    agent_values[path[len(path) - 1]] = agent_values[path[len(path) - 1]] - 1   # reduce the value of the giver

    hypothetical_nsw = split_nsw(agent_values)                                  # evaluate the nsw with these values

    return hypothetical_nsw                     # since the path has not actually been done, the nsw is hypothetical


def calculate_item_envy_relations(preferences, allocation):
    """
    This function finds the edges that our graph contains.
    To do this, we check the envy relations between our agents.
    This returns all relations, including duplicates, and therefore contains multi-graph information.
    """

    big_envy_item_list = []             # will contain all envy relations between all agents

    for i in range(0, agent_quantity):  # we put all  envied items by all agents into the "big_envy_item_list"
        big_envy_item_list.append(envy_list(preferences, i, allocation))    # each agents' likings are collected
        # we now find the envied agents from these envied items
        # after all, the edges for our envy graph are relations between agents, not items

    envy_graph_edges = envied_agents(big_envy_item_list, allocation)
    # this turns the envied items into envied agents

    return envy_graph_edges


def envy_list(preferences, x, allocation):
    """
    This function takes a specific agent and finds all items that they like, but others possess.
    Note that this function is called for each agent and only calculates the result for one agent.
    Thus, it is called agent_quantity times.
    """

    # save all items that our agent x likes and does not to possess
    envied_items = []

    for item in range(0, item_quantity):                    # we check for all possible items whether an agent:

        if preferences[x][item] and allocation[item] != x:  # likes the item AND does not possess it
            envied_items.append(item)

    return envied_items


def envied_agents(envied_items, allocation):
    """
    This function receives the knowledge of which-agent-envies-which-item- and turns it into
    which-agent-envies-which-agent.
    This yields the envy-edges for the envy-graph.
    """

    all_agents_envies = []                                  # this will contain a list for each agent.

    for specific_agent in range(0, len(envied_items)):      # for all agents

        this_agent_envies = []                              # this particular agent has specific envies to others

        for specific_item in envied_items[specific_agent]:  # find the specific envies to others

            this_agent_envies.append(allocation[specific_item])
            # this yields the envied agent who has the specific_item of our specific_agent

        all_agents_envies.append(this_agent_envies)
        # this appends all the envies of a specific agent, is called for each agent => contains all envy-edges!

    return all_agents_envies


def find_path(apsp_matrix, allocation):
    """
    This function receives the APSP matrix and tries every path to return the best swapping.
    It does so by brute forcing every SP and calculating its NSW Improvement.
    """

    best_path = []                                                      # currently unknown
    current_maximum = 0                                                 # currently zero
    current_nsw = split_nsw(calculate_agent_valuations(allocation))     # current nsw of allocation

    for node in apsp_matrix:                                            # for all agents
        for path in node:                                               # for all paths of an agent
            if bool(path):                                              # if path not empty

                possible_maximum = fast_nsw(path, allocation)           # how good is that path

                if possible_maximum > current_maximum:                  # if it's better, we have new best path
                    best_path = path                                    # best path is return value
                    current_maximum = possible_maximum                  # new maximum reached

    if current_maximum > current_nsw:                                   # if new maximum is better than NO reallocation
        pass

    else:
        best_path = []  # if we don't find a better path, we return an empty list

    print("After checking all entries in the APSP matrix, we have found the best path for reallocation:")
    print_best_path(best_path)
    print("We will now reallocate along this path and generate a new APSP solution.\n\n")
    return best_path


def runtime(agent_quantity, item_quantity):
    """
    This function returns the maximum runtime, as claimed in the paper.
    It is used in printing statements only.
    """

    runtime = 2 * agent_quantity * (item_quantity + 1) * log(agent_quantity * item_quantity)

    return runtime


def bfs(shortened_envy_relation, start_node):
    """
    Implementation of Breadth-First-Search (BFS) partly using code from:
    https://www.algorithms-and-technologies.com/de/breitensuche/Python
    """

    queue = [start_node]                        # this queue contains our nodes (agents) left to visit
    visited = [False] * agent_quantity          # a boolean array indicating whether we have already visited a node
    visited[start_node] = True                  # the start node is already visited
    distances = ["inf"] * agent_quantity        # sets starting distances to other nodes to infinity
    distances[start_node] = 0                   # the distance to the start node is 0
    shortest_paths_to_node = []                 # initialises the SP list

    for i in range(0, agent_quantity):
        shortest_paths_to_node.append([])       # fill the SP list with agent many sublists for each SP

    while len(queue) > 0:                       # while there are nodes left

        node = queue.pop(0)                     # pop the current node

        # this code is executed for each node of the envy-graph

        for i in range(0, len(shortened_envy_relation[node])):          # for each of its neighbours
            if not visited[shortened_envy_relation[node][i]]:           # if we didn't visit the neighbour yet

                visited[shortened_envy_relation[node][i]] = True        # mark it as visited
                distances[shortened_envy_relation[node][i]] = distances[node] + 1
                # set distance to neighbour to (1 + node before)
                shortest_paths_to_node[shortened_envy_relation[node][i]] = shortest_paths_to_node[node] + [node]
                # we note the path to the neighbour. It is the path to the node before plus the current node.
                queue.append(shortened_envy_relation[node][i])          # put all neighbors in the queue

    # Now, we have finished the bfs and "clean" our results

    for i in range(0, agent_quantity):
        # this loop appends the last node of a path to all paths, so we get complete paths
        if i != start_node:         # except to itself, as we don't need a path to the start node
            shortest_paths_to_node[i].append(i)

            if distances[i] == "inf":           # if there was no path from a node to another node, the path is empty
                shortest_paths_to_node[i] = []

    return shortest_paths_to_node


def solve_APSP(shortened_envy_relation):
    """
    This function solves the APSP problem using our implementation of bfs.
    We do this by solving SP from each node separately.
    It returns a pseudo-matrix containing the APSP solution.
    """

    solution_matrix = []                                             # will contain shortest paths for each agent-pair

    for agent in range(0, agent_quantity):                           # for each agent run bfs
        solution_matrix.append(bfs(shortened_envy_relation, agent))  # bfs yield for that agent is saved

    print("Die APSP Matrix looks like this:")
    for shortest_path_to_node in solution_matrix:
        print(shortest_path_to_node)
    print()
    return solution_matrix


def shorten_envy_list(agent_edges_list):
    """
    This function shortens the envy relations by the agents.
    Until now, these envy relations were unsorted and contained duplicates.
    Returns a sorted envy relation without duplicates.
    """

    shortened_envy_relation = [0] * agent_quantity              # create new, empty envy list

    for i in range(0, len(agent_edges_list)):                   # iterate over all agents' envies

        agent_edges_list[i].sort()                              # sort this agents' envy list
        short_envy = list(dict.fromkeys(agent_edges_list[i]))   # delete duplicates from this list
        shortened_envy_relation[i] = short_envy                 # put tidy envy list in big envy list

    return shortened_envy_relation                              # return complete and now tidy envy list


def pick_items(best_path, changing_allocation, possessions, preferences):
    """
    This function finds a list of possible items to be swapped in order to reallocate along a given best path.
    """

    swapping_item_list = []                                         # will contain items to reallocate

    for agent in range(0, len(best_path) - 1):                      # we need |path|-1 many items to swap

        count = 0

        for giveable_item in possessions[best_path[agent + 1]]:     # check all items that the giver has

            count = count + 1

            if preferences[best_path[agent]][giveable_item]:        # if the taker likes it

                swapping_item_list.append(giveable_item)            # we save the item for this pair of agents

                break

    return swapping_item_list


def find_possession(allocation):
    """
    This function creates a list of possessions for each agent.
    It is used in printing only, as it is easily readable.
    """

    possessions = []

    for agent in range(0, agent_quantity):  # create empty possession list so each agent has their own possession list

        possessions.append([])

    for item in range(0, len(allocation)):  # run through the items and note who owns what

        possessions[allocation[item]].append(item)

    return possessions


def execute_swap(changing_allocation, swapping_list, best_path):
    """
    This function executes the swapping list.
    It returns a new and improved allocation.
    """

    for item in range(0, len(swapping_list)):   # each item becomes reallocated

        changing_allocation[swapping_list[item]] = best_path[item]
        # allocate the item from the list to the agent mentioned in the path

    return changing_allocation


def print_preferences(preferences):
    """
    This function prettily prints the agents preferences.
    """

    print("\n These are the preferences of the agents:\n")
    count = 0

    for agent in preferences:
        print("Agent", count, "likes:", agent)
        count = count + 1
    print()

    return 0


def print_possession(possessions):
    """
    This function prettily prints the agents' possessions.
    """

    print("\n These are the items of the agents:\n")
    count = 0

    for agent in possessions:
        print("Agent", count, "has:", agent)
        count = count + 1
    print()

    return 0


def print_envy(all_agents_envies):
    """
    This function prettily prints the agents' envy relation.
    """

    print("\n This is the envy information of the agents:\n")
    count = 0

    for agent in all_agents_envies:
        print("Agent", count, "envies these agents:", agent)
        count = count + 1
    print()

    return 0


def print_best_path(best_path):
    """
    This function prettily prints the best_path'.
    """

    reversed_list = best_path[::-1]
    print(reversed_list)

    return 0


def final_print(allocation, time, maximalzeit):
    """
    This function prints a bunch of information at the end.
    """

    print("Optimum gefunden. Beende Programm.")
    print("This is the final possession:", find_possession(allocation))
    print("The NSW of this allocation is:", split_nsw(calculate_agent_valuations(allocation)))
    print("Wir haben", time, "von maximal", maximalzeit, "Tauschungen benötigt!")

    return 0


def main():
    """
    This function manages everything.

    In part one, it initialises the preferences of all agents and provides an allocation.

    Then, it prints a bunch of useful information regarding our instance. This can be used to backcheck the solution.

    In part three, an envy-relation is computed by comparing the agents with each other.
    This relation is the edge set of our graph.
    With bfs from each agent, we solve the APSP problem.
    Each of these paths become evaluated and the best one is returned.
    We calculate the necessary items for this augmentation and execute it.
    After this, we calculate the new edge set and the process repeats.
    """

    # ### PART ONE - CREATE INSTANCE ### #
    preferences = create_agent_preferences(create_agents(agent_quantity))  # creates preferences
    allocation = random_allocation(preferences)  # calls allocation function

    # ### PART TWO - PRINT INSTANCE INFORMATION ### #
    print()
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print("This is our problem information:")
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print("The parameters for this run were:\n", "n =", agent_quantity, ",m =", item_quantity, ",p =", liking_probability)
    print_preferences(preferences)
    print_possession(find_possession(allocation))
    all_agents_envies = calculate_item_envy_relations(preferences, allocation)
    shortened_envy_relation = shorten_envy_list(all_agents_envies)
    print_envy(shortened_envy_relation)
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print("The program will now solve the instance...")
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")

    # ### PART THREE - SOLVE INSTANCE ### #
    global_swapping_list = []

    for run in range(0, round(runtime(agent_quantity, item_quantity))):

        all_agents_envies = calculate_item_envy_relations(preferences, allocation)
        shortened_envy_relation = shorten_envy_list(all_agents_envies)

        apsp_matrix = solve_APSP(shortened_envy_relation)  # solve APSP
        best_path = find_path(apsp_matrix, allocation)     # the best path is found by searching the APSP solution

        if not best_path:  # if the best path is empty, aka we have found the optimal allocation

            print("These are all the items, that have been swapped:\n", global_swapping_list)
            print("After solving, the agents now own different items.")
            print_possession(find_possession(allocation))

            return 0

        swapping_plan = pick_items(best_path, allocation, find_possession(allocation), preferences)
        # we will now find an item swapping list that matches this path
        global_swapping_list.append(swapping_plan)

        allocation = execute_swap(allocation, swapping_plan, best_path)
        # now we execute that swapping list and yield a new allocation

    return 0


# ###### Code ######

if __name__ == "__main__":
    main()
