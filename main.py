import requests
import feedparser
import pandas as pd
from datetime import date, timedelta

URL = "http://export.arxiv.org/api/query"


def fetch_arxiv_papers(query, start, max_results):
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",  # Sort the results by submission date
        "sortOrder": "descending",  # Get the most recent papers first
    }

    response = requests.get(URL, params=params)

    if response.status_code == 200:
        # Parse the Atom data using feedparser
        parsed_data = feedparser.parse(response.text)
        return parsed_data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    # Calculate the date range for the last year
    today = date.today()
    last_year = today - timedelta(days=365)
    last_year_str = last_year.strftime("%Y-%m-%d")

    # Construct the initial query with other search criteria
    # don't care about AI, multimedia (MM), 
    query = f"all:blockchain%20NOT%20cat:cs.AI%20NOT%20cat:cs.MM%20NOT%20cat:cs.CY"
    results_per_iteration = 100
    total_results = 1000  # Adjust this based on the number of papers you want to fetch

    print(f"Searching arXiv for papers submitted in the last year")

    papers_list = []
    category_counts = {}

    for i in range(0, total_results, results_per_iteration):
        papers_data = fetch_arxiv_papers(query, i, results_per_iteration)

        if papers_data:
            for entry in papers_data.entries:
                title = entry.title
                published_date = entry.published

                # Check if the paper's submission date is within the last year
                if published_date >= last_year_str:

                    # Get the categories for the paper
                    categories = [cat.term for cat in entry.tags if cat.term.startswith("cs.")]
                    #categories = categories = [cat.term for cat in entry.tags]

                    # Access the author affiliations
                    #affiliations = [author.get('arxiv_affiliation', '') for author in entry.authors]

                    if categories:
                        # Access the author affiliations
                        # affiliations = []
                        # for author in entry.authors:
                        #     for affiliation in author.get('arxiv_affiliation', []):
                        #         affiliations.append(affiliation)

                        papers_list.append({
                            'Title': title,
                            'Published Date': published_date,
                            'Categories': categories,
                            #'Affiliations': affiliations
                        })

                        # Count the occurrences of each category
                        for category in categories:
                            category_counts[category] = category_counts.get(category, 0) + 1

                            #print(title)
                else:
                    # Exit the loop if we reached papers submitted before the last year
                    break

        else:
            print("Error fetching data.")
            break

    # Convert the list of dictionaries to a pandas DataFrame
    papers_df = pd.DataFrame(papers_list)

    # Print the number of results in the DataFrame
    print(f"Number of results: {papers_df.shape[0]}")

    # Print the list of categories and their counts
    print("Category Counts:")
    for category, count in category_counts.items():
        print(f"{category}: {count}")

    # Save the DataFrame to a CSV file
    papers_df.to_csv('papers.csv', index=False)

    print("Data saved successfully.")
