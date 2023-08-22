from flask import Flask, request, jsonify
import asyncio
import aiohttp

app = Flask(__name__)

async def fetch_data(url, session):
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("numbers", [])
    except (aiohttp.ClientError, asyncio.TimeoutError):
        pass
    return []

async def fetch_and_merge(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(url, session) for url in urls]
        results = await asyncio.gather(*tasks)
        merged_numbers = list(set([num for sublist in results for num in sublist]))
        return merged_numbers

@app.route('/numbers', methods=['GET'])
def get_numbers():
    urls = request.args.getlist('url')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    merged_numbers = loop.run_until_complete(fetch_and_merge(urls))
    
    return jsonify({"numbers": sorted(merged_numbers)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089)
