# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (get_enum_type,
                                                get_location_type,
                                                get_three_state_flag,
                                                tags_type,
                                                resource_group_name_type)
from azure.cli.core.commands.validators import \
    get_default_location_from_resource_group

from ._validators import (validate_appservice_name_or_id,
                          validate_connection_string, validate_datetime,
                          validate_export, validate_import,
                          validate_import_depth, validate_query_fields,
                          validate_feature_query_fields, validate_filter_parameters,
                          validate_separator)


def load_arguments(self, _):

    # PARAMETER REGISTRATION
    fields_arg_type = CLIArgumentType(
        nargs='+',
        help='Customize output fields.',
        validator=validate_query_fields,
        arg_type=get_enum_type(['key', 'value', 'label', 'content_type', 'etag', 'tags', 'locked', 'last_modified'])
    )
    feature_fields_arg_type = CLIArgumentType(
        nargs='+',
        help='Customize output fields for Feature Flags.',
        validator=validate_feature_query_fields,
        arg_type=get_enum_type(['key', 'label', 'locked', 'last_modified', 'state', 'description', 'conditions'])
    )
    filter_parameters_arg_type = CLIArgumentType(
        validator=validate_filter_parameters,
        help="Space-separated filter parameters in 'name[=value]' format.",
        nargs='*'
    )
    datatime_filter_arg_type = CLIArgumentType(
        validator=validate_datetime,
        help='Format: "YYYY-MM-DDThh:mm:ssZ". If no time zone specified, use UTC by default.'
    )
    top_arg_type = CLIArgumentType(
        options_list=['--top', '-t'],
        type=int,
        help='Maximum number of items to return. Must be a positive integer. Default to 100.'
    )

    with self.argument_context('appconfig') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('name', options_list=['--name', '-n'], id_part='None', help='Name of the App Configuration. You can configure the default name using `az configure --defaults app_configuration_store=<name>`', configured_default='app_configuration_store')
        c.argument('connection_string', validator=validate_connection_string, configured_default='appconfig_connection_string',
                   help="Combination of access key and endpoint of App Configuration. Can be found using 'az appconfig credential list'. Users can preset it using `az configure --defaults appconfig_connection_string=<connection_string>` or environment variable with the name AZURE_APPCONFIG_CONNECTION_STRING.")
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.')
        c.argument('datetime', arg_type=datatime_filter_arg_type)
        c.argument('top', arg_type=top_arg_type)
        c.argument('all_', options_list=['--all'], action='store_true', help="List all items.")
        c.argument('fields', arg_type=fields_arg_type)

    with self.argument_context('appconfig create') as c:
        c.argument('location', options_list=['--location', '-l'], arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.ignore('sku')

    with self.argument_context('appconfig update') as c:
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('appconfig credential regenerate') as c:
        c.argument('id_', options_list=['--id'], help='Id of the key to be regenerated. Can be found using az appconfig credential list command.')

    with self.argument_context('appconfig kv import') as c:
        c.argument('label', help="Imported KVs and feature flags will be assigned with this label. If no label specified, will assign null label.")
        c.argument('prefix', help="This prefix will be appended to the front of imported keys. Prefix will be ignored for feature flags.")
        c.argument('source', options_list=['--source', '-s'], arg_type=get_enum_type(['file', 'appconfig', 'appservice']), validator=validate_import, help="The source of importing. Note that importing feature flags from appservice is not supported.")
        c.argument('yes', help="Do not prompt for preview.")
        c.argument('skip_features', help="Import only key values and exclude all feature flags. By default, all feature flags will be imported from file or appconfig. Not applicable for appservice.", arg_type=get_three_state_flag())

    with self.argument_context('appconfig kv import', arg_group='File') as c:
        c.argument('path', help='Local configuration file path. Required for file arguments.')
        c.argument('format_', options_list=['--format'], arg_type=get_enum_type(['json', 'yaml', 'properties']), help='Imported file format. Required for file arguments. Currently, feature flags are only supported in json format.')
        c.argument('depth', validator=validate_import_depth, help="Depth for flattening the json or yaml file to key-value pairs. Flatten to the deepest level by default. Not applicable for property files or feature flags.")
        # bypass cli allowed values limition
        c.argument('separator', validator=validate_separator, help="Delimiter for flattening the json or yaml file to key-value pairs. Required for importing hierarchical structure. Separator will be ignored for property files and feature flags. Supported values: '.', ',', ';', '-', '_', '__', '/', ':' ")

    with self.argument_context('appconfig kv import', arg_group='AppConfig') as c:
        c.argument('src_name', help='The name of the source App Configuration.')
        c.argument('src_connection_string', validator=validate_connection_string, help="Combination of access key and endpoint of the source store.")
        c.argument('src_key', help='If no key specified, import all keys by default. Support star sign as filters, for instance abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported. Key filtering not applicable for feature flags. By default, all feature flags with specified label will be imported.')
        c.argument('src_label', help="Only keys with this label in source AppConfig will be imported. If no label specified, import keys with null label by default.")

    with self.argument_context('appconfig kv import', arg_group='AppService') as c:
        c.argument('appservice_account', validator=validate_appservice_name_or_id, help='ARM ID for AppService OR the name of the AppService, assuming it is in the same subscription and resource group as the App Configuration. Required for AppService arguments')

    with self.argument_context('appconfig kv export') as c:
        c.argument('label', help="Only keys and feature flags with this label will be exported. If no label specified, export keys and feature flags with null label by default.")
        c.argument('prefix', help="Prefix to be trimmed from keys. Prefix will be ignored for feature flags.")
        c.argument('key', help='If no key specified, return all keys by default. Support star sign as filters, for instance abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported. Key filtering not applicable for feature flags. By default, all feature flags with specified label will be exported.')
        c.argument('destination', options_list=['--destination', '-d'], arg_type=get_enum_type(['file', 'appconfig', 'appservice']), validator=validate_export, help="The destination of exporting. Note that exporting feature flags to appservice is not supported.")
        c.argument('yes', help="Do not prompt for preview.")
        c.argument('skip_features', help="Export only key values and exclude all feature flags. By default, all features with the specified label will be exported to file or appconfig. Not applicable for appservice.", arg_type=get_three_state_flag())

    with self.argument_context('appconfig kv export', arg_group='File') as c:
        c.argument('path', help='Local configuration file path. Required for file arguments.')
        c.argument('format_', options_list=['--format'], arg_type=get_enum_type(['json', 'yaml', 'properties']), help='File format exporting to. Required for file arguments. Currently, feature flags are only supported in json format.')
        c.argument('depth', validator=validate_import_depth, help="Depth for flattening the json or yaml file to key-value pairs. Flatten to the deepest level by default. Not appicable for property files or feature flags.")
        # bypass cli allowed values limition
        c.argument('separator', validator=validate_separator, help="Delimiter for flattening the json or yaml file to key-value pairs. Required for importing hierarchical structure. Separator will be ignored for property files and feature flags. Supported values: '.', ',', ';', '-', '_', '__', '/', ':' ")

    with self.argument_context('appconfig kv export', arg_group='AppConfig') as c:
        c.argument('dest_name', help='The name of the destination App Configuration.')
        c.argument('dest_connection_string', validator=validate_connection_string, help="Combination of access key and endpoint of the destination store.")
        c.argument('dest_label', help="Exported KVs will be labeled with this destination label.")

    with self.argument_context('appconfig kv export', arg_group='AppService') as c:
        c.argument('appservice_account', validator=validate_appservice_name_or_id, help='ARM ID for AppService OR the name of the AppService, assuming it is in the same subscription and resource group as the App Configuration. Required for AppService arguments')

    with self.argument_context('appconfig kv set') as c:
        c.argument('key', help='Key to be set.')
        c.argument('label', help="If no label specified, set the key with null label by default")
        c.argument('tags', arg_type=tags_type)
        c.argument('content_type', help='Content type of the keyvalue to be set.')
        c.argument('value', help='Value of the keyvalue to be set.')

    with self.argument_context('appconfig kv delete') as c:
        c.argument('key', help='Support star sign as filters, for instance * means all key and abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported.')
        c.argument('label', help="If no label specified, delete entry with null label. Support star sign as filters, for instance * means all label and abc* means labels with abc as prefix. Similarly, *abc and *abc* are also supported.")

    with self.argument_context('appconfig kv show') as c:
        c.argument('key', help='Key to be showed.')
        c.argument('label', help="If no label specified, show entry with null label. Filtering is not supported.")

    with self.argument_context('appconfig kv list') as c:
        c.argument('key', help='If no key specified, return all keys by default. Support star sign as filters, for instance abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported.')
        c.argument('label', help="If no label specified, list all labels. Support star sign as filters, for instance abc* means labels with abc as prefix. Similarly, *abc and *abc* are also supported. Use '\\0' for null label.")

    with self.argument_context('appconfig kv restore') as c:
        c.argument('key', help='If no key specified, restore all keys by default. Support star sign as filters, for instance abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported.')
        c.argument('label', help="If no label specified, restore all key-value pairs with all labels. Support star sign as filters, for instance abc* means labels with abc as prefix. Similarly, *abc and *abc* are also supported.")

    with self.argument_context('appconfig kv lock') as c:
        c.argument('key', help='Key to be locked.')
        c.argument('label', help="If no label specified, lock entry with null label. Filtering is not supported.")

    with self.argument_context('appconfig kv unlock') as c:
        c.argument('key', help='Key to be unlocked.')
        c.argument('label', help="If no label specified, unlock entry with null label. Filtering is not supported.")

    with self.argument_context('appconfig revision list') as c:
        c.argument('key', help='If no key specified, return all keys by default. Support star sign as filters, for instance abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported.')
        c.argument('label', help="If no label specified, list all labels. Support star sign as filters, for instance abc* means labels with abc as prefix. Similarly, *abc and *abc* are also supported. Use '\\0' for null label.")

    with self.argument_context('appconfig feature show') as c:
        c.argument('feature', help='Name of the feature flag to be retrieved')
        c.argument('label', help="If no label specified, show entry with null label. Filtering is not supported.")
        c.argument('fields', arg_type=feature_fields_arg_type)

    with self.argument_context('appconfig feature set') as c:
        c.argument('feature', help="Name of the feature flag to be set. Only alphanumeric characters, '.', '-' and '_' are allowed.")
        c.argument('label', help="If no label specified, set the feature flag with null label by default")
        c.argument('description', help='Description of the feature flag to be set.')

    with self.argument_context('appconfig feature delete') as c:
        c.argument('feature', help='Key of the feature to be deleted. Support star sign as filters, for instance * means all key and abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported.  Comma separated keys are not supported. Please provide escaped string if your feature name contains comma.')
        c.argument('label', help="If no label specified, delete the feature flag with null label by default. Support star sign as filters, for instance * means all labels and abc* means labels with abc as prefix. Similarly, *abc and *abc* are also supported.")

    with self.argument_context('appconfig feature list') as c:
        c.argument('feature', help='Key of the feature to be listed. Support star sign as filters, for instance * means all key and abc* means keys with abc as prefix. Similarly, *abc and *abc* are also supported. Comma separated keys are not supported. Please provide escaped string if your feature name contains comma.')
        c.argument('label', help="If no label specified, list all labels. Support star sign as filters, for instance * means all labels and abc* means labels with abc as prefix. Similarly, *abc and *abc* are also supported. Use '\\0' for null label.")
        c.argument('fields', arg_type=feature_fields_arg_type)
        c.argument('all_', help="List all feature flags.")

    with self.argument_context('appconfig feature lock') as c:
        c.argument('feature', help='Key of the feature to be locked.')
        c.argument('label', help="If no label specified, lock the feature flag with null label by default.")

    with self.argument_context('appconfig feature unlock') as c:
        c.argument('feature', help='Key of the feature to be unlocked.')
        c.argument('label', help="If no label specified, unlock the feature flag with null label by default.")

    with self.argument_context('appconfig feature enable') as c:
        c.argument('feature', help='Key of the feature to be enabled.')
        c.argument('label', help="If no label specified, enable the feature flag with null label by default.")

    with self.argument_context('appconfig feature disable') as c:
        c.argument('feature', help='Key of the feature to be disabled.')
        c.argument('label', help="If no label specified, disable the feature flag with null label by default.")

    with self.argument_context('appconfig feature filter add') as c:
        c.argument('feature', help='Name of the feature to which you want to add the filter.')
        c.argument('label', help="If no label specified, add to the feature flag with null label by default.")
        c.argument('filter_name', help='Name of the filter to be added.')
        c.argument('filter_parameters', arg_type=filter_parameters_arg_type)
        c.argument('index', type=int, help='Zero-based index in the list of filters where you want to insert the new filter. If no index is specified or index is invalid, filter will be added to the end of the list.')

    with self.argument_context('appconfig feature filter delete') as c:
        c.argument('feature', help='Name of the feature from which you want to delete the filter.')
        c.argument('label', help="If no label specified, delete from the feature flag with null label by default.")
        c.argument('filter_name', help='Name of the filter to be deleted.')
        c.argument('index', type=int, help='Zero-based index of the filter to be deleted in case there are multiple instances with same filter name.')
        c.argument('all_', help="Delete all filters associated with a feature flag.")

    with self.argument_context('appconfig feature filter show') as c:
        c.argument('feature', help='Name of the feature which contains the filter.')
        c.argument('label', help="If no label specified, show the feature flag with null label by default.")
        c.argument('filter_name', help='Name of the filter to be displayed.')
        c.argument('index', type=int, help='Zero-based index of the filter to be displayed in case there are multiple instances with same filter name.')

    with self.argument_context('appconfig feature filter list') as c:
        c.argument('feature', help='Name of the feature whose filters you want to be displayed.')
        c.argument('label', help="If no label specified, display filters from the feature flag with null label by default.")
        c.argument('all_', help="List all filters associated with a feature flag.")
