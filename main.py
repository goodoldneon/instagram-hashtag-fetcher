import argparse
import datetime
import csv
import time
from typing import Any, Dict, List, Optional, Union

import requests


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def convert_timestamp_to_string(ts: Optional[int]) -> str:
    if ts is None:
        return ""

    return datetime.datetime.utcfromtimestamp(ts).strftime(DATETIME_FORMAT)


def get_post_from_node(
    node: Dict[str, Any]
) -> Dict[str, Optional[Union[bool, float, int, str]]]:
    """
    Convert each node (a.k.a. post) into an easy-to-use dict.
    """

    post_id = node.get("id", None)
    owner_id = node.get("owner", {}).get("id", None)

    created_time = convert_timestamp_to_string(
        node.get("taken_at_timestamp", None)
    )

    typename = node.get("__typename")
    comment_count = node.get("edge_media_to_comment", {}).get("count", None)
    like_count = node.get("edge_liked_by", {}).get("count", None)
    video_view_count = node.get("video_view_count", None)
    shortcode = node.get("shortcode", None)

    caption = (
        node.get("edge_media_to_caption", {})
        .get("edges", [{}])[0]
        .get("node", {})
        .get("text", None)
    )

    return {
        "id": post_id,
        "owner_id": owner_id,
        "created_time": created_time,
        "typename": typename,
        "comment_count": comment_count,
        "like_count": like_count,
        "video_view_count": video_view_count,
        "shortcode": shortcode,
        "caption": caption,
    }


def get_posts(
    tag: str, min_datetime: datetime.datetime, wait: int,
) -> List[Dict[str, Any]]:
    """
    Fetch data from Instagram's API.

    - The data can only be fetched in batches, so we'll repeatedly fetch using
        a `while` loop. The `while` loop will only end when we get a post whose
        creation time is before the `min_datetime`.
    - The response data is deeply nested and not easy to work with, so we'll
        use our `get_post_from_node` function to extract a simple dict.
    - Each response includes an `end_cursor`, which we'll use to get the next
        batch.
    """

    all_posts: List[Dict[str, Any]] = []
    endpoint = f"https://www.instagram.com/explore/tags/{tag}/?__a=1"
    end_cursor = ""
    earliest_datetime_so_far = datetime.datetime.now()

    while min_datetime < earliest_datetime_so_far:
        url = endpoint

        if end_cursor:
            print(f"Waiting {wait} seconds...")
            time.sleep(wait)
            print(f'Using cursor "{end_cursor}"')
            url += f"&max_id={end_cursor}"

        """
        This `try` block is mainly for gracefully handling rate limits. If we
        hit a rate limit, an exception will be raised. Instead of crashing the
        program (and losing all the data we've fetched so far), we want to stop
        fetching and just export what we got.
        """
        try:
            print("Fetching...")
            res = requests.get(url)
            data = res.json()

            end_cursor = data["graphql"]["hashtag"]["edge_hashtag_to_media"][
                "page_info"
            ]["end_cursor"]

            edges = data["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]
            posts = [get_post_from_node(edge.get("node")) for edge in edges]
        except Exception as e:
            print("The program was interrupted by an exception")
            print(e)
            break

        if len(posts) == 0:
            print("No posts")
            break

        all_posts += posts

        earliest_datetime_so_far = min(
            [
                datetime.datetime.strptime(
                    post["created_time"], DATETIME_FORMAT
                )
                for post in posts
                if isinstance(post["created_time"], str)
            ]
        )

        print("{} medias fetched so far".format(len(all_posts)))

    print("Completed fetching")

    return all_posts


def export_posts(posts: List[Dict[str, Any]], output_path: str) -> None:
    if len(posts) > 0:
        print("Exporting posts...")

        with open(output_path, "w") as f:
            writer = csv.writer(f, delimiter="|")
            column_names = list(posts[0].keys())
            writer.writerow(column_names)

            for m in posts:
                writer.writerow(list(m.values()))
    else:
        print("Nothing to export")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Instagram post data for a hashtag. "
            "This program will fetch posts created between min-date and now."
        )
    )

    parser.add_argument("tag", type=str, help="Tag name (without the # symbol)")

    parser.add_argument(
        "min_date",
        metavar="min-date",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
        help="Minimum date (YYYY-MM-DD format)",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="",
        type=str,
        default="data.csv",
        help="CSV output file name",
    )

    parser.add_argument(
        "-w",
        "--wait",
        metavar="",
        type=int,
        default=20,
        help="Seconds to wait between fetches",
    )

    args = parser.parse_args()
    tag = args.tag
    min_date = args.min_date
    output = args.output
    wait = args.wait

    posts = get_posts(tag, min_date, wait)
    export_posts(posts, output_path=output)


main()
