from storage import movie_storage_sql as storage
import statistics
import random
import requests
from html import escape


API_KEY = "716b39d"

def main():
    """
    Initializing the movie dictionary and starts the control menu
    """
    print("\nWelcome to your Movie Database!\n")
    control_menu()


# ---------- option 1 ----------
def list_all_movies() -> None:
    """
    Prints all movies in the collection with their rating and release year.
    """
    movies = storage.list_movies()
    print("*" * 10, "My Movies", "*" * 10)
    print(f"\nThere are {len(movies)} movies in your list!\n")

    for title, info in movies.items():
        rating = info.get("rating", "N/A")
        year = info.get("year", "Unknown")
        poster = info.get("poster", "No poster available")
        print(f"** {title} **")
        print(f"-> Rating: {rating}")
        print(f"-> Release year: {year}")
        print(f"-> Poster: {poster}\n")


# ---------- option 2 ----------
def add_movie() -> None:
    """
    Adds a new movie to the database using OMDb API.
    """
    user_input_movie = input("Please enter the movie title to fetch from OMDb: ").strip()
    movies = storage.list_movies()

    if user_input_movie in movies:
        print(f"{user_input_movie} already exists in your database!")
        return

    # Fetch data from OMDb
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={user_input_movie}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        print("Could not reach OMDb API.")
        return

    data = response.json()
    if data.get("Response") != "True":
        print(f"Movie '{user_input_movie}' not found in OMDb!")
        return

    # Extract relevant data
    movie_title = data.get("Title", user_input_movie)

    # Year
    try:
        year = int(data.get("Year", 0))
    except ValueError:
        year = 0

    # IMDb Rating
    try:
        rating = float(data.get("imdbRating", 0))
    except ValueError:
        rating = 0

    # Poster URL
    poster_url = data.get("Poster", "")

    # Save to database
    storage.add_movie(movie_title, year, rating, poster_url)
    print(f"{movie_title} added to your database successfully!")


# ---------- option 3 ----------
def rename_movie() -> None:
    """
    Renames an existing movie in the database.
    """
    movies = storage.list_movies()
    old_name = input("Please enter the name of the movie you would like to rename: ")

    if old_name not in movies:
        print("That movie doesn't exist.")
        return

    new_name = input("Please enter the new name of the movie: ")
    if new_name in movies:
        print(f"{new_name} already exists in the database. Rename aborted.")
        return

    year = movies[old_name] ["year"]
    rating = movies[old_name] ["rating"]
    poster = movies[old_name].get("poster", "")

    # delete old, insert new
    storage.delete_movie(old_name)
    storage.add_movie(new_name, year, rating, poster)

    print(f"{old_name} has been renamed to {new_name}")


# ---------- option 4 ----------
def update_movie_rating() -> None:
    """
    Changes the rating of an existing movie.
    """
    movies = storage.list_movies()
    movie_name = input("Please enter the name of the movie you would like update the rating for: ")

    if movie_name not in movies:
        print("That movie doesn't exist.")
        return

    try:
        new_rating_float = float(input("Please enter the new rating (1-10): "))
        if not 1 <= new_rating_float <= 10:
            print("Invalid rating.")
            return
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return

    storage.update_movie(movie_name, new_rating_float)
    print(f"Rating for {movie_name} updated to {new_rating_float}")


# ---------- option 5 ----------
def delete_movie() -> None:
    """
    Removes a movie from the database.
    """
    movies = storage.list_movies()
    movie_name = input("Please enter the name of the movie you would like to remove: ")

    if movie_name not in movies:
        print("That movie doesn't exist")
        return

    storage.delete_movie(movie_name)
    print(f"{movie_name} has been deleted.")


# ---------- option 6 ----------
def show_movie_statistics() -> None:
    """
    Calculates and displays statistics like average, median, best and worst movies.
    """
    movies = storage.list_movies()
    # List of all existing ratings
    ratings = [info["rating"] for info in movies.values() if "rating" in info]

    if not ratings:
        print("No ratings available to calculate statistics.")
        return

    average_rating = round(statistics.mean(ratings), 2)
    median_rating = round(statistics.median(ratings), 2)
    max_rating = max(ratings)
    min_rating = min(ratings)

    best_movies = [title for title, info in movies.items() if info["rating"] == max_rating]
    worst_movies = [title for title, info in movies.items() if info["rating"] == min_rating]

    #statistics print
    print(f"\n{'*' * 10} Movies statistics {'*' * 10}\n")
    print(f"Number of rated movies: {len(ratings)}")
    print(f"Average rating: {average_rating}")
    print(f"Median rating: {median_rating}\n")

    print(f"Highest rating: {max_rating}")
    print("Title(s):")
    for title in best_movies:
        print(f" {title}")

    print(f"\nLowest rating: {min_rating}")
    print("Title(s):")
    for title in worst_movies:
        print(f" {title}")


# ---------- option 7 ----------
def show_random_movie() -> None:
    """
    Selects and displays a random movie from the database, including poster URL.
    """
    movies = storage.list_movies()
    if not movies:
        print("No movies in the database.")
        return

    random_movie_title = random.choice(list(movies))
    info = movies[random_movie_title]

    print(f"Your movie for tonight: {random_movie_title}")
    print(f"Rating: {info['rating']}, Release year: {info.get('year', 'Unknown')}")
    print(f"Poster: {info.get('poster', 'No poster available')}")


# ---------- option 8 ----------
def search_movie() -> None:
    """
    Searches for a movie by name or substring (case-insensitive) and displays it if found,
    including poster URL.
    """
    movies = storage.list_movies()
    search_term = input("Please enter the name or part of the movie: ").lower()

    result = []
    for title, info in movies.items():
        if search_term in title.lower():
            poster = info.get("poster", "No poster available")
            result.append(f"{title:<40} | "
                          f"Rating: {info['rating']:<4} | "
                          f"Release year: {info.get('year', 'Unknown')} |"
                          f"Poster: {poster}"
                          )

    if result:
        print("\nMovie(s) found:\n")
        for movie in result:
            print(movie)
    else:
        print(f"No movie found with '{search_term}' in it.")


# ---------- option 9 ----------
def generate_website():
    """
    Generates an HTML website from the movies in the database.
    """
    movies = storage.list_movies()  # Get all movies from the database

    # 1) Read the template file
    try:
        with open("_static/index_template.html", "r", encoding="utf-8") as file:
            template = file.read()
    except FileNotFoundError:
        print("Template file not found. Make sure _static/index_template.html exists.")
        return

    # 2) Build the <li> items matching style.css (movie-poster, movie-title, movie-year)
    items = []
    for title, data in movies.items():
        poster = (data.get("poster") or "").strip()
        # OMDb sometimes returns "N/A"
        if not poster or poster.upper() == "N/A":
            # Optional: put a placeholder file next to index.html or use a remote placeholder
            poster = "https://placehold.co/128x193?text=No+Poster"

        year = data.get("year", "Unknown")
        rating = data.get("rating", "N/A")

        items.append(f"""
<li>
  <div class="movie">
    <img class="movie-poster" src="{poster}" alt="{escape(title)} poster"/>
    <div class="movie-title">{escape(title)}</div>
    <div class="movie-year">{escape(str(year))} • Rating: {escape(str(rating))}</div>
  </div>
</li>
""")

    movie_grid = "\n".join(items)

    # 3) Replace placeholders in the template
    website_html = template.replace("__TEMPLATE_TITLE__", "My Movie Database")
    website_html = website_html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    # 4) Write the final HTML to a file (root folder)
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(website_html)

    # 5) Print success message
    print("Website was generated successfully.")


    # 3 Replace placeholders in the template
    website_html = template.replace("__TEMPLATE_TITLE__", "My Movie Database")
    website_html = website_html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    # 4 Write the final HTML to a file
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(website_html)

    # 5 Print success message
    print("Website was generated successfully.")


def list_movies_by_rating() -> None:
    """
    Sorts and displays all movies in descending order by rating, including poster URL.
    """
    movies = storage.list_movies()
    if not movies:
        print("No movies in database.")
        return

    # descending order from worst to best rated
    sorted_movies = sorted(movies.items(), key=lambda item: item[1]["rating"], reverse=True)

    print(f"\n{'*' * 10} Movies sorted by rating (best to worst) {'*' * 10}")
    for title, info in sorted_movies:
        poster = info.get("poster", "No poster available")
        print(f"{title:<40} | Rating: {info['rating']:<4} | "
              f"Release year: {info.get('year', 'Unknown')} |"
              f"Poster: {poster}"
              )


def control_menu():
    """
    Displays the control menu and handels user input.
    """
    menu_options = [
        "0. Exit",
        "1. Show all movies",
        "2. Add movie",
        "3. Rename movie",
        "4. Change movie rating",
        "5. Delete movie",
        "6. Statistics",
        "7. Random movie",
        "8. Search movie",
        "9. Generate website",
        "10. Movies sorted by rating",
    ]

    while True:
        print("\nWhat would you like to do? \n")
        for options in menu_options:
            print(f" {options}")

        user_choice = input("\nPlease enter your choice (0-10): ")

        if user_choice == "0":
            print("Bye!")
            break
        elif user_choice == "1":
            list_all_movies()
        elif user_choice == "2":
            add_movie()
        elif user_choice == "3":
            rename_movie()
        elif user_choice == "4":
            update_movie_rating()
        elif user_choice == "5":
            delete_movie()
        elif user_choice == "6":
            show_movie_statistics()
        elif user_choice == "7":
            show_random_movie()
        elif user_choice == "8":
            search_movie()
        elif user_choice == "9":
            generate_website()
        elif user_choice == "10":
            list_movies_by_rating()
        else:
            print(f"{user_choice} is not a valid choice")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
