class QueryParser:
    @staticmethod
    def parse(query_string):
        params = {}
        pairs = query_string.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
        return params
