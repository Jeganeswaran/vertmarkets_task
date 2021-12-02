import asyncio
import json
import requests


class MagazineStoreSubscribers:
    """
    This program identifies all subscribers that are subscribed to at least one magazine in each category.
    """

    def __init__(self):
        self.token = ""
        self.base_url = "http://magazinestore.azurewebsites.net/api/"
        self.category = []
        self.subscribers = []

    async def get_request_api(self, url):
        res = requests.get(url)
        if res.status_code == 200:
            result = res.json()
            if result['success']:
                self.token = result['token']
                return result

        raise Exception

    async def submit_request_api(self, url, data):
        headers = {
            'Content-Type': 'application/json'
        }
        res = requests.post(url, headers=headers, data=json.dumps(data))
        if res.status_code == 200:
            result = res.json()
            if result['success']:
                self.token = result['token']
                return result

        raise Exception

    async def getRequestToken(self):
        url = self.base_url + "token"
        await self.get_request_api(url)
        return self.token

    async def get_categories(self):
        url = self.base_url + "categories/{token}".format(token=self.token)

        result = await self.get_request_api(url)
        for category in result['data']:
            url = self.base_url + "magazines/{token}/{category}".format(token=self.token, category=category)
            response = await self.get_request_api(url)
            magazines = [x['id'] for x in response['data']]
            self.category.append({"category": category, "magazines": magazines})
        return self.category

    async def get_subscribers(self):
        url = self.base_url + "subscribers/{token}".format(token=self.token)
        result = await self.get_request_api(url)
        if result:
            self.subscribers = result['data']
            return result['data']
        return None

    async def main(self):
        await self.getRequestToken()
        tasks = [task if isinstance(task, asyncio.Task) else asyncio.create_task(task)
                 for task in [self.get_categories(), self.get_subscribers()]]
        categories, subscribers = await asyncio.gather(*tasks)

        subscribed_user = []
        for subscriber in subscribers:
            is_append = 0
            for category in categories:
                result = set(subscriber['magazineIds']) & set(category['magazines'])
                if result:
                    is_append += 1
            if is_append == len(categories):
                subscribed_user.append(subscriber['id'])

        result = await self.submit_request_api(self.base_url + "answer/{}".format(self.token),
                                               {"subscribers": subscribed_user})
        print(subscribers)
        print(result)


if __name__ == '__main__':
    # Creating object for class
    store = MagazineStoreSubscribers()

    # async call class methods 
    asyncio.run(store.main())
