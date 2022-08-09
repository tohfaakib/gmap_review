# google map reviews scraper


## Instructions
### Install dependencies
```bash
pip install -r requirements.txt
```

### Usage
####Help:
```bash
python3 google_maps_reviews_scraper.py --help
```

####Example:
```bash
python3 google_maps_reviews_scraper.py -u https://www.google.com/maps/place/Victoria+and+Albert+Museum/@51.4966392,
-0.17218,15z/data\=\!4m5\!3m4\!1s0x0:0x9eb7094dfdcd651f\!8m2\!3d51.4966392\!4d-0.17218 -n 5000 -o "reviews_sample1" -v "headless = False"
```