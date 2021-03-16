import datetime

from singer.utils import DATETIME_PARSE

BOOKMARK_FIELD = 'updated_at'

def get_stream_metadata(stream):
    # TODO - will the stream metadata breadcrumb always be in position [0]?
    #  If so, we can simplify this logic to:
    # self.catalog.metadata[0]
    breadcrumbs = [item['breadcrumb'] for item in stream['metadata']]
    idx_empty_breadcrumb = breadcrumbs.index([])
    return stream['metadata'][idx_empty_breadcrumb]['metadata']


def validate_args(args):

    if args.state:

        bookmarks = args.state.get('bookmarks')

        for bookmark in bookmarks.keys():

            if bookmarks[bookmark]['field'] != BOOKMARK_FIELD:
                raise ValueError(f'The only bookmark field implemented is: {BOOKMARK_FIELD}')

            try:
                date_text = bookmarks[bookmark]['last_record']
                datetime.datetime.strptime(date_text, DATETIME_PARSE)
            except ValueError:
                raise ValueError("Unable to parse as datetime.")

    if args.catalog:

        streams = args.catalog.to_dict()['streams']

        for stream in streams:
            metadata = get_stream_metadata(stream)
            replication_method = metadata.get('replication-method')
            replication_key = metadata.get('replication-key')

            if replication_key is not None and not isinstance(replication_key, str):
                raise ValueError(f"Replication key cannot be a composite key; "
                                 f"got {replication_key} for stream {stream}")

            if replication_method not in ['INCREMENTAL', 'FULL_TABLE', None]:
                raise ValueError(f"Unknown replication method: {replication_method} for stream {stream}")

            if replication_method == 'INCREMENTAL' and replication_key is None:
                raise ValueError(f"Missing replication key for replication key INCREMENTAL for stream {stream}")

            if replication_method in ['FULL_TABLE', None] and replication_key is not None:
                raise ValueError(f"Unexpected replication key found: {replication_key} for stream {stream}")

    return args

