from dotenv import load_dotenv
from notion_client import AsyncClient
from notion_client.helpers import collect_paginated_api
import aiohttp
import asyncio
import os

load_dotenv()


class NotionDatabase:
    def __init__(self, database_id:str) -> None:
        self._database_id = database_id
        self._notion = AsyncClient(auth=os.getenv('NOTION'))
        self._property_extractors = {
        'url': lambda v: v.get('url'),
        'rich_text': lambda v: v['rich_text'][0].get('text', {}).get('content') if v.get('rich_text') else None,
        'title': lambda v: v['title'][0].get('text', {}).get('content') if v.get('title') else None,
        'multi_select': lambda v: [item['name'] for item in v.get('multi_select', [])],
        'number': lambda v: v.get('number'),
        'select': lambda v: v.get('select', {}).get('name'),
        'email': lambda v: v.get('email'),
        'phone_number': lambda v: v.get('phone_number'),
        'date': lambda v: v.get('date', {}).get('start'),
        'checkbox': lambda v: v.get('checkbox'),
        'files': lambda v: v.get('files', []),
        'people': lambda v: v.get('people', []),
        'relation': lambda v: v.get('relation', []),
        'rollup': lambda v: v.get('rollup', {}).get('array', []),
        }
    @staticmethod
    async def async_iterate_paginated_api(function, **kwargs):
        """Async generator for paginated API."""
        # Initialize start_cursor to None (to fetch the first page)
        start_cursor = None
        
        while True:
            # Call the function with the start_cursor as part of the kwargs
            response = await function(start_cursor=start_cursor, **kwargs)
            
            # Yield the results from the current page
            for result in response.get("results"):
                yield result

            # Check if there are more pages
            if not response.get("has_more"):
                break

            # Update start_cursor to the next page
            start_cursor = response.get("next_cursor")

    @staticmethod
    async def collect_paginated_api(function, **kwargs):
        """Collect all paginated results into a list."""
        all_results = []
        
        # Use the async generator to iterate over all paginated results
        async for result in NotionDatabase.async_iterate_paginated_api(function, **kwargs):
            all_results.append(result)
        
        return all_results
    async def get_notion_data(self):
        all_results = await NotionDatabase.collect_paginated_api(
            self._notion.databases.query, database_id=self._database_id
        )
        for page in all_results:
            page_id = page.get('id', '')
            properties = page.get('properties', {})
            extracted_data = {'page_id': page_id}

            # Extract all properties based on their types
            for prop_name, prop_data in properties.items():
                prop_type = prop_data.get('type')
                extractor = self._property_extractors.get(prop_type, lambda v: None)
                extracted_data[prop_name] = {extractor(prop_data):prop_type}

            yield extracted_data
    async def insert_notion_data(self, data: dict):
        page_id = data.get('page_id')
        updated_properties = {}

        # Define a mapping from property_type to the function handling the update
        property_handlers = {
            'rich_text': lambda key, value: {"rich_text": [{"text": {"content": str(value) if value else ""}}]},
            'url': lambda key, value: {"url": value if value else None},
            'title': lambda key, value: {"title": [{"text": {"content": str(value) if value else ""}}]},
            'checkbox': lambda key, value: {"checkbox": bool(value)},
            'number': lambda key, value: {"number": int(value) if value is not None else None},
            'select': lambda key, value: {"select": {"name": str(value) if value else None}},
            'multi_select': lambda key, value: {"multi_select": [{"name": str(item) if item else ""} for item in value] if value else []},
            'date': lambda key, value: {"date": {"start": value['start'], "end": value.get('end', None)} if value else None},
            'email': lambda key, value: {"email": str(value) if value else ""},
            'phone_number': lambda key, value: {"phone_number": str(value) if value else ""},
            'people': lambda key, value: {"people": [{"id": person_id} for person_id in value] if value else []},
            'relation': lambda key, value: {"relation": [{"id": relation_id} for relation_id in value] if value else []}
        }

        for key, value in data.items():
            if key == 'page_id':
                continue

            # Extract the property type and the actual value
            property_type = list(value.values())[0]  # Get the property type
            actual_value = list(value.keys())[0]  # Get the actual content value

            print(property_type,actual_value)
            # Ensure value is not null or None, and use the handler from the property_handlers dict
            if property_type in property_handlers:
                updated_properties[key] = property_handlers[property_type](key, actual_value)
            else:
                # If the property type is not recognized, we set it to None explicitly
                updated_properties[key] = None


        response = await self._notion.pages.update(
            page_id=page_id,
            properties=updated_properties
        )

        return response




    # async def insert_notion_data(self, data:dict):
    #     tasks = []
    #     all_results = await NotionDatabase.collect_paginated_api(
    #         self._notion.databases.query, database_id=self._database_id
    #     )
    #     for result in all_results:
    #         page_id = result.get('id')
    #         properties_dict = result.get('properties')
    #         updated_properties = {}
    #         for target_column,value in data.items():
    #             if properties_dict and target_column in properties_dict:
    #                 print("existing")
    #                 target_value = properties_dict[target_column]
    #                 target_property_type = target_value.get('type')

    #                 target_property_value = self._property_extractors.get(target_property_type, lambda v: None)(target_value)
    #                 if target_property_value:
            
    #                     column = properties_dict.get(target_column)
    #                     if column:
    #                         property_type = column.get('type')
    #                         property_value = self._property_extractors.get(property_type, lambda v: None)(column)
    #                         if property_value:  
    #                             if value:
    #                                 if property_type == 'url':
    #                                     updated_properties[target_column] = {
    #                                         "url": value
    #                                     }
    #                                 elif property_type == 'rich_text':
    #                                     updated_properties[target_column] = {
    #                                         "rich_text": [
    #                                             {
    #                                                 "text": {
    #                                                     "content":value
    #                                                 }
    #                                             }
    #                                         ]
    #                                     }
    #                                 elif property_type == 'multi_select':
    #                                     updated_properties[target_column] = {
    #                                         "multi_select": [
    #                                             {"name":value}
    #                                         ]
    #                                     }
    #                                 elif property_type == 'title':
    #                                     updated_properties[target_column] = {
    #                                         "title": [
    #                                             {
    #                                                 "text": {
    #                                                     "content":value
    #                                                 }
    #                                             }
    #                                         ]
    #                                     }
    #         print(updated_properties)
    #         if updated_properties:      
    #             tasks.append(
    #                 self._notion.pages.update(
    #                     page_id=page_id,
    #                     properties=updated_properties
    #                 )
    #         )
    #     print(f"Updated page_id {page_id} with {updated_properties}")


        # await asyncio.gather(*tasks)

