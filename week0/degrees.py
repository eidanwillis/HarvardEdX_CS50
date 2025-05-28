import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():

    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    
    """
    Should return the shortest path from the person with id 'source' to the person with the id 'target'
    Assuming there is a path from source to target, your function should return a list
    where each list item is the next '(movie_id, person_id)' pair in the path from the source to target.
    Each pair should be a tuple of strings.

    E.g. if return value of shortest_path were (1, 2), (3, 4), this means source (person_id1) starred
    in movie 1 with person 2, person 2 starred in movie 3 with person 4, and person 4 is the target (person_id2)

    If no possible path, return 'None'.

    May call 'neighbors_for_person' function which accepts a person's id as input and returns a set of
    '(movie_id, person_id) pairs for all people who starred in a movie with the given person.

    Reviewing our datasets, we have:

    movie.csv with variables: movie id, title, year of release
    people.csv with variables: person id, name, birth year
    stars.csv with variables: person id, movie id

    stars.csv is our connection to understand which people starred in which movies, and it will
    also be our way of understanding the degree of connection between various actors

    """
    # set variables
    source_id = source
    target_id = target

    # create a queue and add the source id to it
    queue = QueueFrontier()
    queue.add(source_id)

    # create a set to store visited ids
    visited = set() # set of visited ids

    # create a dictionary to store the path
    path = {} # dictionary of paths

    # add the source id to the path
    # path[source_id] = None  # path[source_id] = None means the source id has no path to the target id

    # while the queue is not empty
    while not queue.empty():
        # remove the first id from the queue
        current_id = queue.remove()

        # if the current id is the target id, return the path
        if current_id == target_id:
            # create a list to store the path with movie_id and person_id as tuples
            path_list = []
            # while the current id is not the source id
            while current_id != source_id:
                # add the current id to the path list
                for movie_id in people[path[current_id][1]]["movies"]:
                    if movie_id == path[current_id][0]:
                        new_row = [movie_id, current_id]
                        print(new_row)
                        path_list.append(new_row)
                # update the current id to the previous id
                current_id = path[current_id][1]
            # reverse the path list
            path_list.reverse()

            print("A list of movies and people in the path from " + people[source_id]["name"] + " (" + source_id + ")" + " to " + people[target_id]["name"] + 
                            " (" + target_id + ")" + " are: \n")
            print("\nPath List:")
            print("Movie ID | Person ID")
            print("---------|-----------")
            for movie, person in path_list:
                print(f"{movies[movie]['title']} ({movie}) | {people[person]['name']} ({person})")
            print("\n")
            # return the path list
            return path_list
        else:
            pass

        # get the neighbors of the current id
        neighbors = neighbors_for_person(current_id)

        # for each neighbor
        for movie_id, person_id in neighbors:
            # if the neighbor is not in the visited set
            if person_id not in visited:
                # add the neighbor to the visited set
                visited.add(person_id)
                # add the neighbor to the path
                path[person_id] = (movie_id, current_id)
                # add the neighbor to the queue
                queue.add(person_id)    
    # if no path is found, return None
    return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

if __name__ == "__main__":
    main()




