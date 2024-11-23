import requests
import numpy as np
import heapq
import itertools

def get_coordinate(place_names):

    coordinates = []
    for place_name in place_names:
        url = f'https://dapi.kakao.com/v2/local/search/keyword.json?query={place_name}'
        headers = {
            "Authorization": "KakaoAK 27e3e2bffed2464908e54ca9b2062cd9"
        }
        try:
            info = requests.get(url, headers=headers).json()['documents'][0]
            coordinates.append({'lon': float(info['x']), 'lat': float(info['y'])})
        except IndexError:
            print(f"No result found for {place_name}")
        except Exception as e:
            print(f"Error occurred: {e}")

    return coordinates

def get_distance_matrix(coordinates):

    tmap_api_key = "4zEO17lmTn1GfYU4fKQV60ml2mfXu806LyXmGhW1"
    tmap_distance_url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json"
    n = len(coordinates)
    distance_matrix = np.zeros((n, n))

    headers = {
        "Content-Type": "application/json",
        "appKey": tmap_api_key
    }

    for i in range(n):
        for j in range(n):
            if i != j:
                payload = {
                    "startX": coordinates[i]['lon'],
                    "startY": coordinates[i]['lat'],
                    "endX": coordinates[j]['lon'],
                    "endY": coordinates[j]['lat'],
                    "reqCoordType": "WGS84GEO",
                    "resCoordType": "WGS84GEO",
                    "startName": "출발지",
                    "endName": "도착지"
                }
                try:
                    response = requests.post(tmap_distance_url, json=payload, headers=headers)
                    if response.status_code == 200:
                        # Get the total distance by summing all section distances
                        route_sections = response.json().get("features", [])
                        total_distance = sum(
                            feature["properties"]["distance"] for feature in route_sections if "distance" in feature["properties"]
                        )
                        if total_distance > 0:
                            distance_matrix[i][j] = total_distance
                        else:
                            print(f"No valid distance found for points {i} to {j}.")
                            distance_matrix[i][j] = np.inf
                    else:
                        print(f"Error {response.status_code}: {response.text}")
                        distance_matrix[i][j] = np.inf
                except Exception as e:
                    print(f"Error occurred: {e}")
                    distance_matrix[i][j] = np.inf

    return distance_matrix

def astar_shortest_path(place_names, start_index=0):

    # Fetch coordinates
    coordinates = get_coordinate(place_names)
    if not coordinates:
        print("No valid coordinates found.")
        return None, float("inf")

    # Compute distance matrix
    distance_matrix = get_distance_matrix(coordinates)

    n = len(distance_matrix)
    current_path = [start_index]
    current_distance = 0

    # Priority queue: (estimated_cost, current_distance, path)
    queue = [(0, current_distance, current_path)]

    best_path = None
    min_distance = float("inf")

    while queue:
        estimated_cost, distance_so_far, path = heapq.heappop(queue)

        # If all nodes are visited, terminate without returning to start
        if len(path) == n:
            if distance_so_far < min_distance:
                min_distance = distance_so_far
                best_path = path
            continue

        # Expand to neighbors
        last_node = path[-1]
        for neighbor in range(n):
            if neighbor not in path:  # Check if the node has been visited
                new_path = path + [neighbor]
                new_distance = distance_so_far + distance_matrix[last_node][neighbor]

                # Estimated cost: current distance + heuristic (minimum edge cost)
                estimated_distance = new_distance + min(
                    [distance_matrix[neighbor][i] for i in range(n) if i not in new_path] + [0]
                )
                heapq.heappush(queue, (estimated_distance, new_distance, new_path))

    return [place_names[i] for i in best_path], min_distance

def tsp_shortest_path(place_names):

    # Fetch coordinates
    coordinates = get_coordinate(place_names)
    if not coordinates:
        print("No valid coordinates found.")
        return None, float("inf")

    # Compute distance matrix
    distance_matrix = get_distance_matrix(coordinates)

    n = len(distance_matrix)
    best_path = None
    min_cost = float("inf")

    # Generate all permutations of the nodes (excluding the starting node)
    for perm in itertools.permutations(range(1, n)):
        current_path = [0] + list(perm) + [0]  # Start and end at node 0
        current_cost = 0
        for i in range(len(current_path) - 1):
            current_cost += distance_matrix[current_path[i]][current_path[i + 1]]

        if current_cost < min_cost:
            min_cost = current_cost
            best_path = current_path

    return [place_names[i] for i in best_path], min_cost

# Example usage
place_names = ["계족산 황톳길", "대청호반", "동춘당", "엑스포과학공원"]

astar_path, astar_distance = astar_shortest_path(place_names)
print("A* Shortest Path:", astar_path)
print("A* Total Distance:", astar_distance)

tsp_path, tsp_distance = tsp_shortest_path(place_names)
print("TSP Shortest Circular Path:", tsp_path)
print("TSP Total Distance:", tsp_distance)
