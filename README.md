# Instagram Hashtag Fetcher

Fetch Instagram posts with a specific hashtag.

## Getting Started

1. Python 3 must be installed.
2. Create a virtual environment.
   - Run `python -m venv .venv`
3. Activate the virtual environment.
   - Run `source .venv/bin/activate`
4. Install the dependencies.
   - Run `pip install -r requirements.txt`

## Usage

To fetch posts with the `#plasticsurgery` hashtag created on 5/16/2020 or later, run:

```
python main.py plasticsurgery 2020-05-16
```

By default, this program will export to `data.csv`. You can specify a different output file like this:

```
python main.py plasticsurgery 2020-05-16 -o foo.csv
```

The output CSV file will contain columns delimited by the `|` symbol.

## Known Issues

### Data Fetching Ends Too Soon

The Instagram API endpoint is supposed to return posts in descending chronological order, but sometimes an old post is included. Since this program will stop when it encounters a post below the specified `min_time`, this old post will cause the program to stop early.

A possible solution is to stop when the median post creation time is below the `min_time`.

### Data Always Starts With the Latest Post

The Instagram API endpoint doesn't support time filters. Consequently, this program will always fetch data up to the latest post. In other words, you can't say "I want posts between dates X and Y".

## Help

```
python main.py --help
```
