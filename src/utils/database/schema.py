from datetime import datetime
import traceback


class Schema():

    @staticmethod
    def laptop_price(data: dict) -> dict:
        schema = {
            'brand': 'str',
            'cpu': 'str',
            'screen_size': 'str',
            'screen_resolution': 'str',
            'memory': 'str',
            'storage': 'str',
            'graphic_type': 'str',
            'graphic_name': 'str',
            'weight': 'str',
            'battery': 'str',
            'refresh_rate': 'str',
            'price': 'float',
        }
        # Verify all keys exist in the schema
        must_have_keys = schema.keys()

        for key in must_have_keys:
            if key not in data.keys():
                return {
                    'status': 'error',
                    'message': f'Key "{key}" is missing',
                    'data': None,
                }

        for key in data.keys():
            if key not in must_have_keys:
                return {
                    'status': 'error',
                    'message': f'Key "{key}" is not in schema',
                    'data': None,
                }

        # Verify date data to follow schema
        try:
            for key, value in data.items():
                if key not in schema:
                    raise ValueError(f'Key "{key}" is not in schema')
                if not isinstance(value, eval(schema[key])):
                    raise ValueError(f'Value "{value}" of key "{key}" is correct in type: {schema[key]}')
        except Exception as e:
            print(traceback.format_exc())
            return {
                'status': 'error',
                'message': str(e),
                'data': None,
            }

        # return the data with the correct schema

        return {
            'status': 'success',
            'message': 'Data is valid',
            'data': data,
        }


if __name__ == '__main__':
    # Sample data
    data = {
        'brand': 'Apple',
        'cpu': 'Intel Core i7',
        'screen_size': '16"',
        'screen_resolution': '3072 x 1920',
        'memory': '16 GB',
        'storage': '512 GB SSD',
        'graphic_type': 'Integrated Card',
        'graphic_name': 'Intel Iris Plus Graphics',
        'weight': '4.3 lbs.',
        'battery': '100 Wh',
        'refresh_rate': '60 Hz',
        'price': 2199.00,
    }

    # Validate data
    result = Schema.laptop_price(data)

    # Print result
    print(result)
