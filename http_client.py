import aiohttp
import asyncio


async def getPage(session, url):
    response = {
        'success': False,
        'url': url,
        'resText': ''
    }
    try:
        async with session.get(url) as res:
            response['success'] = True
            response['resText'] = await res.text()
            return response
    except Exception:
        return response


async def getAllPages(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(getPage(session, url))
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses


async def init(urls):
    async with aiohttp.ClientSession() as session:
        data = await getAllPages(session, urls)
        return data


def makeParallelReq(urls):
    return asyncio.run(init(urls))