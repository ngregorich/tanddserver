# tanddlogger

This repo contains a demo of a data logger for the [TandD](https://tandd.com), TR72A (replaced with the [TR72A2](https://tandd.com/product/tr72a2/)) temperature and humidity sensor

The sensor can automatically upload to the free [TandD WebStorage Service](https://webstorage-service.com) or to a [Windows server application](https://tandd.com/software/td-data-server.html), but I wanted something with more flexibility and less Windows, so I developed my own server using [Python](https://www.python.org) [Flask](https://flask.palletsprojects.com/en/stable/)

I documented my efforts on this project on [this blog post]()

## Installation

1. Install [Astral uv](https://docs.astral.sh/uv/getting-started/installation/)
    1. Recently I've been using [mise-en-place](https://mise.jdx.dev/) (not required)
        1. In this case you can install `uv` with `mise use --global uv`
2. Clone this repo

## Usage

1. Change into the repo directory
2. Start the data logger: `uv run tanddserver.py`
3. Configure the TandD sensors to upload data to your server's IP address via http
4. Monitor `log.csv`

## Contributing

Please feel free to file an Issue or PR

## License

[MIT](LICENSE.md)
