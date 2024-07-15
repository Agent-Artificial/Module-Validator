# Python Functions Documentation

**`from_nano`**

## **Docstring:**
```
Converts from nano to j
```

## **Parameters:**
- `amount`: `int`

## **Returns:** `float`

---

**`to_nano`**

## **Docstring:**
```
Converts from j to nano
```

## **Parameters:**
- `amount`: `float`

## **Returns:** `int`

---

**`from_horus`**

## **Docstring:**
```
Converts from horus to j
```

## **Parameters:**
- `amount`: `int`
- `subnet_tempo`: `int`

## **Returns:** `float`

---

**`repr_j`**

## **Docstring:**
```
Given an amount in nano, returns a representation of it in tokens/J.

E.g. "103.2J".
```

## **Parameters:**
- `amount`: `int`

## **Returns:** `None specified`

---

**`get_node_url`**

## **Parameters:**
- `comx_settings`: `ComxSettings | None`

## **Returns:** `str`

---

**`get_available_nodes`**

## **Parameters:**
- `comx_settings`: `ComxSettings | None`

## **Returns:** `list[str]`

---

**`format_balance`**

## **Docstring:**
```
Formats a balance.
```

## **Parameters:**
- `balance`: `int`
- `unit`: `BalanceUnit`

## **Returns:** `str`

---

**`intersection_update`**

## **Docstring:**
```
Update a dictionary with another dictionary, but only with keys that are already present.
```

## **Parameters:**
- `base`: `dict[K, V]`
- `update`: `dict[K, Z]`

## **Returns:** `Mapping[K, V | Z]`

---

**`is_ss58_address`**

## **Docstring:**
```
Validates whether the given string is a valid SS58 address.

Args:
    address: The string to validate.
    ss58_format: The SS58 format code to validate against.

Returns:
    True if the address is valid, False otherwise.
```

## **Parameters:**
- `address`: `str`
- `ss58_format`: `int`

## **Returns:** `TypeGuard[Ss58Address]`

---

**`check_ss58_address`**

## **Docstring:**
```
Validates whether the given string is a valid SS58 address.

Args:
    address: The string to validate.
    ss58_format: The SS58 format code to validate against.

Returns:
    The validated SS58 address.

Raises:
    AssertionError: If the address is invalid.
```

## **Parameters:**
- `address`: `str | Ss58Address`
- `ss58_format`: `int`

## **Returns:** `Ss58Address`

---

**`generate_keypair`**

## **Docstring:**
```
Generates a new keypair.
```

## **Parameters:**
None

## **Returns:** `Keypair`

---

**`__init__`**

## **Parameters:**
- `self`
- `value`: `T`

## **Returns:** `None specified`

---

**`connections`**

## **Docstring:**
```
Gets the maximum allowed number of simultaneous connections to the
network node.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_conn`**

## **Docstring:**
```
Context manager to get a connection from the pool.

Tries to get a connection from the pool queue. If the queue is empty,
it blocks for `timeout` seconds until a connection is available. If
`timeout` is None, it blocks indefinitely.

Args:
    timeout: The maximum time in seconds to wait for a connection.

Yields:
    The connection object from the pool.

Raises:
    QueueEmptyError: If no connection is available within the timeout
      period.
```

## **Parameters:**
- `self`
- `timeout`: `float | None`
- `init`: `bool`

## **Returns:** `None specified`

---

**`_get_storage_keys`**

## **Parameters:**
- `self`
- `storage`: `str`
- `queries`: `list[tuple[str, list[Any]]]`
- `block_hash`: `str | None`

## **Returns:** `None specified`

---

**`_get_lists`**

## **Docstring:**
```
Generates a list of tuples containing parameters for each storage function based on the given functions and substrate interface.

Args:
    functions (dict[str, list[query_call]]): A dictionary where keys are storage module names and values are lists of tuples.
        Each tuple consists of a storage function name and its parameters.
    substrate: An instance of the SubstrateInterface class used to interact with the substrate.

Returns:
    A list of tuples in the format `(value_type, param_types, key_hashers, params, storage_function)` for each storage function in the given functions.

Example:
    >>> _get_lists(
            functions={'storage_module': [('storage_function', ['param1', 'param2'])]},
            substrate=substrate_instance
        )
    [('value_type', 'param_types', 'key_hashers', ['param1', 'param2'], 'storage_function'), ...]
```

## **Parameters:**
- `self`
- `storage_module`: `str`
- `queries`: `list[tuple[str, list[Any]]]`
- `substrate`: `SubstrateInterface`

## **Returns:** `list[tuple[Any, Any, Any, Any, str]]`

---

**`_send_batch`**

## **Docstring:**
```
Sends a batch of requests to the substrate and collects the results.

Args:
    substrate: An instance of the substrate interface.
    batch_payload: The payload of the batch request.
    request_ids: A list of request IDs for tracking responses.
    results: A list to store the results of the requests.
    extract_result: Whether to extract the result from the response.

Raises:
    NetworkQueryError: If there is an `error` in the response message.

Note:
    No explicit return value as results are appended to the provided 'results' list.
```

## **Parameters:**
- `self`
- `batch_payload`: `list[Any]`
- `request_ids`: `list[int]`
- `extract_result`: `bool`

## **Returns:** `None specified`

---

**`_make_request_smaller`**

## **Docstring:**
```
Splits a batch of requests into smaller batches, each not exceeding the specified maximum size.

Args:
    batch_request: A list of requests to be sent in a batch.
    max_size: Maximum size of each batch in bytes.

Returns:
    A list of smaller request batches.

Example:
    >>> _make_request_smaller(batch_request=[('method1', 'params1'), ('method2', 'params2')], max_size=1000)
    [[('method1', 'params1')], [('method2', 'params2')]]
```

## **Parameters:**
- `self`
- `batch_request`: `list[tuple[T1, T2]]`
- `prefix_list`: `list[list[str]]`
- `fun_params`: `list[tuple[Any, Any, Any, Any, str]]`

## **Returns:** `tuple[list[list[tuple[T1, T2]]], list[Chunk]]`

---

**`_are_changes_equal`**

## **Parameters:**
- `self`
- `change_a`: `Any`
- `change_b`: `Any`

## **Returns:** `None specified`

---

**`_rpc_request_batch`**

## **Docstring:**
```
Sends batch requests to the substrate node using multiple threads and collects the results.

Args:
    substrate: An instance of the substrate interface.
    batch_requests : A list of requests to be sent in batches.
    max_size: Maximum size of each batch in bytes.
    extract_result: Whether to extract the result from the response message.

Returns:
    A list of results from the batch requests.

Example:
    >>> _rpc_request_batch(substrate_instance, [('method1', ['param1']), ('method2', ['param2'])])
    ['result1', 'result2', ...]
```

## **Parameters:**
- `self`
- `batch_requests`: `list[tuple[str, list[Any]]]`
- `extract_result`: `bool`

## **Returns:** `list[str]`

---

**`_rpc_request_batch_chunked`**

## **Docstring:**
```
Sends batch requests to the substrate node using multiple threads and collects the results.

Args:
    substrate: An instance of the substrate interface.
    batch_requests : A list of requests to be sent in batches.
    max_size: Maximum size of each batch in bytes.
    extract_result: Whether to extract the result from the response message.

Returns:
    A list of results from the batch requests.

Example:
    >>> _rpc_request_batch(substrate_instance, [('method1', ['param1']), ('method2', ['param2'])])
    ['result1', 'result2', ...]
```

## **Parameters:**
- `self`
- `chunk_requests`: `list[Chunk]`
- `extract_result`: `bool`

## **Returns:** `None specified`

---

**`_decode_response`**

## **Docstring:**
```
Decodes a response from the substrate interface and organizes the data into a dictionary.

Args:
    response: A list of encoded responses from a substrate query.
    function_parameters: A list of tuples containing the parameters for each storage function.
    last_keys: A list of the last keys used in the substrate query.
    prefix_list: A list of prefixes used in the substrate query.
    substrate: An instance of the SubstrateInterface class.
    block_hash: The hash of the block to be queried.

Returns:
    A dictionary where each key is a storage function name and the value is another dictionary.
    This inner dictionary's key is the decoded key from the response and the value is the corresponding decoded value.

Raises:
    ValueError: If an unsupported hash type is encountered in the `concat_hash_len` function.

Example:
    >>> _decode_response(
            response=[...],
            function_parameters=[...],
            last_keys=[...],
            prefix_list=[...],
            substrate=substrate_instance,
            block_hash="0x123..."
        )
    {'storage_function_name': {decoded_key: decoded_value, ...}, ...}
```

## **Parameters:**
- `self`
- `response`: `list[str]`
- `function_parameters`: `list[tuple[Any, Any, Any, Any, str]]`
- `prefix_list`: `list[Any]`
- `block_hash`: `str`

## **Returns:** `dict[str, dict[Any, Any]]`

---

**`query_batch`**

## **Docstring:**
```
Executes batch queries on a substrate and returns results in a dictionary format.

Args:
    substrate: An instance of SubstrateInterface to interact with the substrate.
    functions (dict[str, list[query_call]]): A dictionary mapping module names to lists of query calls (function name and parameters).

Returns:
    A dictionary where keys are storage function names and values are the query results.

Raises:
    Exception: If no result is found from the batch queries.

Example:
    >>> query_batch(substrate_instance, {'module_name': [('function_name', ['param1', 'param2'])]})
    {'function_name': 'query_result', ...}
```

## **Parameters:**
- `self`
- `functions`: `dict[str, list[tuple[str, list[Any]]]]`

## **Returns:** `dict[str, str]`

---

**`query_batch_map`**

## **Docstring:**
```
Queries multiple storage functions using a map batch approach and returns the combined result.

Args:
    substrate: An instance of SubstrateInterface for substrate interaction.
    functions (dict[str, list[query_call]]): A dictionary mapping module names to lists of query calls.

Returns:
    The combined result of the map batch query.

Example:
    >>> query_batch_map(substrate_instance, {'module_name': [('function_name', ['param1', 'param2'])]})
    # Returns the combined result of the map batch query
```

## **Parameters:**
- `self`
- `functions`: `dict[str, list[tuple[str, list[Any]]]]`
- `block_hash`: `str | None`

## **Returns:** `dict[str, dict[Any, Any]]`

---

**`query`**

## **Docstring:**
```
Queries a storage function on the network.

Sends a query to the network and retrieves data from a
specified storage function.

Args:
    name: The name of the storage function to query.
    params: The parameters to pass to the storage function.
    module: The module where the storage function is located.

Returns:
    The result of the query from the network.

Raises:
    NetworkQueryError: If the query fails or is invalid.
```

## **Parameters:**
- `self`
- `name`: `str`
- `params`: `list[Any]`
- `module`: `str`

## **Returns:** `Any`

---

**`query_map`**

## **Docstring:**
```
Queries a storage map from a network node.

Args:
    name: The name of the storage map to query.
    params: A list of parameters for the query.
    module: The module in which the storage map is located.

Returns:
    A dictionary representing the key-value pairs
      retrieved from the storage map.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `name`: `str`
- `params`: `list[Any]`
- `module`: `str`
- `extract_value`: `bool`

## **Returns:** `dict[Any, Any]`

---

**`compose_call`**

## **Docstring:**
```
Composes and submits a call to the network node.

Composes and signs a call with the provided keypair, and submits it to
the network. The call can be a standard extrinsic or a sudo extrinsic if
elevated permissions are required. The method can optionally wait for
the call's inclusion in a block and/or its finalization.

Args:
    fn: The function name to call on the network.
    params: A dictionary of parameters for the call.
    key: The keypair for signing the extrinsic.
    module: The module containing the function.
    wait_for_inclusion: Wait for the call's inclusion in a block.
    wait_for_finalization: Wait for the transaction's finalization.
    sudo: Execute the call as a sudo (superuser) operation.

Returns:
    The receipt of the submitted extrinsic, if
      `wait_for_inclusion` is True. Otherwise, returns a string
      identifier of the extrinsic.

Raises:
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `fn`: `str`
- `params`: `dict[str, Any]`
- `key`: `Keypair | None`
- `module`: `str`
- `wait_for_inclusion`: `bool`
- `wait_for_finalization`: `bool | None`
- `sudo`: `bool`
- `unsigned`: `bool`

## **Returns:** `ExtrinsicReceipt`

---

**`compose_call_multisig`**

## **Docstring:**
```
Composes and submits a multisignature call to the network node.

This method allows the composition and submission of a call that
requires multiple signatures for execution, known as a multisignature
call. It supports specifying signatories, a threshold of signatures for
the call's execution, and an optional era for the call's mortality. The
call can be a standard extrinsic, a sudo extrinsic for elevated
permissions, or a multisig extrinsic if multiple signatures are
required. Optionally, the method can wait for the call's inclusion in a
block and/or its finalization. Make sure to pass all keys,
that are part of the multisignature.

Args:
    fn: The function name to call on the network. params: A dictionary
    of parameters for the call. key: The keypair for signing the
    extrinsic. signatories: List of SS58 addresses of the signatories.
    Include ALL KEYS that are part of the multisig. threshold: The
    minimum number of signatories required to execute the extrinsic.
    module: The module containing the function to call.
    wait_for_inclusion: Whether to wait for the call's inclusion in a
    block. wait_for_finalization: Whether to wait for the transaction's
    finalization. sudo: Execute the call as a sudo (superuser)
    operation. era: Specifies the call's mortality in terms of blocks in
    the format
        {'period': amount_blocks}. If omitted, the extrinsic is
        immortal.

Returns:
    The receipt of the submitted extrinsic if `wait_for_inclusion` is
    True. Otherwise, returns a string identifier of the extrinsic.

Raises:
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `fn`: `str`
- `params`: `dict[str, Any]`
- `key`: `Keypair`
- `signatories`: `list[Ss58Address]`
- `threshold`: `int`
- `module`: `str`
- `wait_for_inclusion`: `bool`
- `wait_for_finalization`: `bool | None`
- `sudo`: `bool`
- `era`: `dict[str, int] | None`

## **Returns:** `ExtrinsicReceipt`

---

**`transfer`**

## **Docstring:**
```
Transfer amount to destination using key
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `amount`: `float`
- `dest`: `str`

## **Returns:** `None specified`

---

**`transfer_multiple`**

## **Docstring:**
```
Transfers specified amounts of tokens from the signer's account to
multiple target accounts.

The `destinations` and `amounts` lists must be of the same length.

Args:
    key: The keypair associated with the sender's account.
    destinations: A list of SS58 addresses of the recipients.
    amounts: Amount to transfer to each recipient, in nanotokens.
    netuid: The network identifier.

Returns:
    A receipt of the transaction.

Raises:
    InsufficientBalanceError: If the sender's account does not have
      enough balance for all transfers.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `destinations`: `list[Ss58Address]`
- `amounts`: `list[int]`
- `netuid`: `str | int`

## **Returns:** `ExtrinsicReceipt`

---

**`stake`**

## **Docstring:**
```
Stake amount to destination using key
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `amount`: `float`
- `dest`: `str`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`unstake`**

## **Docstring:**
```
Unstake amount from destination using key
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `amount`: `float`
- `dest`: `str`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`update_module`**

## **Docstring:**
```
Updates the parameters of a registered module.

The delegation fee must be an integer between 0 and 100.

Args:
    key: The keypair associated with the module's account.
    name: The new name for the module. If None, the name is not updated.
    address: The new address for the module.
        If None, the address is not updated.
    delegation_fee: The new delegation fee for the module,
        between 0 and 100.
    netuid: The network identifier.

Returns:
    A receipt of the module update transaction.

Raises:
    InvalidParameterError: If the provided parameters are invalid.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `name`: `str`
- `address`: `str`
- `metadata`: `str | None`
- `delegation_fee`: `int`
- `netuid`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`register_module`**

## **Docstring:**
```
Registers a new module in the network.

Args:
    key: The keypair used for registering the module.
    name: The name of the module. If None, a default or previously
        set name is used. # How does this work?
    address: The address of the module. If None, a default or
        previously set address is used. # How does this work?
    subnet: The network subnet to register the module in.
    min_stake: The minimum stake required for the module, in nanotokens.
        If None, a default value is used.

Returns:
    A receipt of the registration transaction.

Raises:
    InvalidParameterError: If the provided parameters are invalid.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `name`: `str`
- `address`: `str | None`
- `subnet`: `str`
- `min_stake`: `int | None`
- `metadata`: `str | None`

## **Returns:** `ExtrinsicReceipt`

---

**`vote`**

## **Docstring:**
```
Casts votes on a list of module UIDs with corresponding weights.

The length of the UIDs list and the weights list should be the same.
Each weight corresponds to the UID at the same index.

Args:
    key: The keypair used for signing the vote transaction.
    uids: A list of module UIDs to vote on.
    weights: A list of weights corresponding to each UID.
    netuid: The network identifier.

Returns:
    A receipt of the voting transaction.

Raises:
    InvalidParameterError: If the lengths of UIDs and weights lists
        do not match.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `uids`: `list[int]`
- `weights`: `list[int]`
- `netuid`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`update_subnet`**

## **Docstring:**
```
Update a subnet's configuration.

It requires the founder key for authorization.

Args:
    key: The founder keypair of the subnet.
    params: The new parameters for the subnet.
    netuid: The network identifier.

Returns:
    A receipt of the subnet update transaction.

Raises:
    AuthorizationError: If the key is not authorized.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `params`: `SubnetParams`
- `netuid`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`transfer_stake`**

## **Docstring:**
```
Transfers stake of key from point A to point B
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `amount`: `float`
- `from_key`: `str`
- `dest`: `str`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`multiunstake`**

## **Docstring:**
```
Unstakes tokens from multiple module keys.

And the lists `keys` and `amounts` must be of the same length. Each
amount corresponds to the module key at the same index.

Args:
    key: The keypair associated with the unstaker's account.
    keys: A list of SS58 addresses of the module keys to unstake from.
    amounts: A list of amounts to unstake from each module key,
      in nanotokens.
    netuid: The network identifier.

Returns:
    A receipt of the multi-unstaking transaction.

Raises:
    MismatchedLengthError: If the lengths of keys and amounts lists do
    not match. InsufficientStakeError: If any of the module keys do not
    have enough staked tokens. ChainTransactionError: If the transaction
    fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `keys`: `list[Ss58Address]`
- `amounts`: `list[int]`
- `netuid`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`multistake`**

## **Docstring:**
```
Stakes tokens to multiple module keys.

The lengths of the `keys` and `amounts` lists must be the same. Each
amount corresponds to the module key at the same index.

Args:
    key: The keypair associated with the staker's account.
    keys: A list of SS58 addresses of the module keys to stake to.
    amounts: A list of amounts to stake to each module key,
        in nanotokens.
    netuid: The network identifier.

Returns:
    A receipt of the multi-staking transaction.

Raises:
    MismatchedLengthError: If the lengths of keys and amounts lists
        do not match.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `keys`: `list[Ss58Address]`
- `amounts`: `list[int]`
- `netuid`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`add_profit_shares`**

## **Docstring:**
```
Allocates profit shares to multiple keys.

The lists `keys` and `shares` must be of the same length,
with each share amount corresponding to the key at the same index.

Args:
    key: The keypair associated with the account
        distributing the shares.
    keys: A list of SS58 addresses to allocate shares to.
    shares: A list of share amounts to allocate to each key,
        in nanotokens.

Returns:
    A receipt of the profit sharing transaction.

Raises:
    MismatchedLengthError: If the lengths of keys and shares
        lists do not match.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `keys`: `list[Ss58Address]`
- `shares`: `list[int]`

## **Returns:** `ExtrinsicReceipt`

---

**`add_subnet_proposal`**

## **Docstring:**
```
Submits a proposal for creating or modifying a subnet within the
network.

The proposal includes various parameters like the name, founder, share
allocations, and other subnet-specific settings.

Args:
    key: The keypair used for signing the proposal transaction.
    params: The parameters for the subnet proposal.
    netuid: The network identifier.

Returns:
    A receipt of the subnet proposal transaction.

Raises:
    InvalidParameterError: If the provided subnet
        parameters are invalid.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `params`: `SubnetParams`
- `ipfs`: `str`
- `netuid`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`add_custom_proposal`**

## **Docstring:**
```
Adds a custom proposal to a specific subnet.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `cid`: `str`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`add_custom_subnet_proposal`**

## **Docstring:**
```
Submits a proposal for creating or modifying a custom subnet within the
network.

The proposal includes various parameters like the name, founder, share
allocations, and other subnet-specific settings.

Args:
    key: The keypair used for signing the proposal transaction.
    params: The parameters for the subnet proposal.
    netuid: The network identifier.

Returns:
    A receipt of the subnet proposal transaction.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `cid`: `str`
- `netuid`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`add_global_proposal`**

## **Docstring:**
```
Submits a proposal for altering the global network parameters.

Allows for the submission of a proposal to
change various global parameters
of the network, such as emission rates, rate limits, and voting
thresholds. It is used to
suggest changes that affect the entire network's operation.

Args:
    key: The keypair used for signing the proposal transaction.
    params: A dictionary containing global network parameters
            like maximum allowed subnets, modules,
            transaction rate limits, and others.

Returns:
    A receipt of the global proposal transaction.

Raises:
    InvalidParameterError: If the provided network
        parameters are invalid.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `params`: `NetworkParams`
- `cid`: `str | None`

## **Returns:** `ExtrinsicReceipt`

---

**`vote_on_proposal`**

## **Docstring:**
```
Casts a vote on a specified proposal within the network.

Args:
    key: The keypair used for signing the vote transaction.
    proposal_id: The unique identifier of the proposal to vote on.

Returns:
    A receipt of the voting transaction in nanotokens.

Raises:
    InvalidProposalIDError: If the provided proposal ID does not
        exist or is invalid.
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `proposal_id`: `int`
- `agree`: `bool`

## **Returns:** `ExtrinsicReceipt`

---

**`unvote_on_proposal`**

## **Docstring:**
```
Retracts a previously cast vote on a specified proposal.

Args:
    key: The keypair used for signing the unvote transaction.
    proposal_id: The unique identifier of the proposal to withdraw the
        vote from.

Returns:
    A receipt of the unvoting transaction in nanotokens.

Raises:
    InvalidProposalIDError: If the provided proposal ID does not
        exist or is invalid.
    ChainTransactionError: If the transaction fails to be processed, or
        if there was no prior vote to retract.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `proposal_id`: `int`

## **Returns:** `ExtrinsicReceipt`

---

**`enable_vote_power_delegation`**

## **Docstring:**
```
Enables vote power delegation for the signer's account.

Args:
    key: The keypair used for signing the delegation transaction.

Returns:
    A receipt of the vote power delegation transaction.

Raises:
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`

## **Returns:** `ExtrinsicReceipt`

---

**`disable_vote_power_delegation`**

## **Docstring:**
```
Disables vote power delegation for the signer's account.

Args:
    key: The keypair used for signing the delegation transaction.

Returns:
    A receipt of the vote power delegation transaction.

Raises:
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`

## **Returns:** `ExtrinsicReceipt`

---

**`add_dao_application`**

## **Docstring:**
```
Submits a new application to the general subnet DAO.

Args:
    key: The keypair used for signing the application transaction.
    application_key: The SS58 address of the application key.
    data: The data associated with the application.

Returns:
    A receipt of the application transaction.

Raises:
    ChainTransactionError: If the transaction fails.
```

## **Parameters:**
- `self`
- `key`: `Keypair`
- `application_key`: `Ss58Address`
- `data`: `str`

## **Returns:** `ExtrinsicReceipt`

---

**`query_map_curator_applications`**

## **Parameters:**
- `self`

## **Returns:** `dict[str, dict[str, str]]`

---

**`query_map_proposals`**

## **Docstring:**
```
Retrieves a mappping of proposals from the network.

Queries the network and returns a mapping of proposal IDs to
their respective parameters.

Returns:
    A dictionary mapping proposal IDs
    to dictionaries of their parameters.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, dict[str, Any]]`

---

**`query_map_weights`**

## **Docstring:**
```
Retrieves a mapping of weights for keys on the network.

Queries the network and returns a mapping of key UIDs to
their respective weights.

Args:
    netuid: The network UID from which to get the weights.

Returns:
    A dictionary mapping key UIDs to lists of their weights.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[int, list[int]]`

---

**`query_map_key`**

## **Docstring:**
```
Retrieves a map of keys from the network.

Fetches a mapping of key UIDs to their associated
addresses on the network.
The query can be targeted at a specific network UID if required.

Args:
    netuid: The network UID from which to get the keys.

Returns:
    A dictionary mapping key UIDs to their addresses.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[int, Ss58Address]`

---

**`query_map_address`**

## **Docstring:**
```
Retrieves a map of key addresses from the network.

Queries the network for a mapping of key UIDs to their addresses.

Args:
    netuid: The network UID from which to get the addresses.

Returns:
    A dictionary mapping key UIDs to their addresses.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[int, str]`

---

**`query_map_emission`**

## **Docstring:**
```
Retrieves a map of emissions for keys on the network.

Queries the network to get a mapping of
key UIDs to their emission values.

Returns:
    A dictionary mapping key UIDs to lists of their emission values.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, list[int]]`

---

**`query_map_incentive`**

## **Docstring:**
```
Retrieves a mapping of incentives for keys on the network.

Queries the network and returns a mapping of key UIDs to
their respective incentive values.

Returns:
    A dictionary mapping key UIDs to lists of their incentive values.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, list[int]]`

---

**`query_map_dividend`**

## **Docstring:**
```
Retrieves a mapping of dividends for keys on the network.

Queries the network for a mapping of key UIDs to
their dividend values.

Returns:
    A dictionary mapping key UIDs to lists of their dividend values.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, list[int]]`

---

**`query_map_regblock`**

## **Docstring:**
```
Retrieves a mapping of registration blocks for keys on the network.

Queries the network for a mapping of key UIDs to
the blocks where they were registered.

Args:
    netuid: The network UID from which to get the registration blocks.

Returns:
    A dictionary mapping key UIDs to their registration blocks.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_lastupdate`**

## **Docstring:**
```
Retrieves a mapping of the last update times for keys on the network.

Queries the network for a mapping of key UIDs to their last update times.

Returns:
    A dictionary mapping key UIDs to lists of their last update times.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, list[int]]`

---

**`query_map_total_stake`**

## **Docstring:**
```
Retrieves a mapping of total stakes for keys on the network.

Queries the network for a mapping of key UIDs to their total stake amounts.

Returns:
    A dictionary mapping key UIDs to their total stake amounts.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_stakefrom`**

## **Docstring:**
```
Retrieves a mapping of stakes from various sources for keys on the network.

Queries the network to obtain a mapping of key addresses to the sources
and amounts of stakes they have received.

Args:
    netuid: The network UID from which to get the stakes.

Returns:
    A dictionary mapping key addresses to lists of tuples
    (module_key_address, amount).

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[str, list[tuple[str, int]]]`

---

**`query_map_staketo`**

## **Docstring:**
```
Retrieves a mapping of stakes to destinations for keys on the network.

Queries the network for a mapping of key addresses to the destinations
and amounts of stakes they have made.

Args:
    netuid: The network UID from which to get the stakes.

Returns:
    A dictionary mapping key addresses to lists of tuples
    (module_key_address, amount).

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[str, list[tuple[str, int]]]`

---

**`query_map_stake`**

## **Docstring:**
```
Retrieves a mapping of stakes for keys on the network.

Queries the network and returns a mapping of key addresses to their
respective delegated staked balances amounts.
The query can be targeted at a specific network UID if required.

Args:
    netuid: The network UID from which to get the stakes.

Returns:
    A dictionary mapping key addresses to their stake amounts.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[str, int]`

---

**`query_map_delegationfee`**

## **Docstring:**
```
Retrieves a mapping of delegation fees for keys on the network.

Queries the network to obtain a mapping of key addresses to their
respective delegation fees.

Args:
    netuid: The network UID to filter the delegation fees.

Returns:
    A dictionary mapping key addresses to their delegation fees.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[str, int]`

---

**`query_map_tempo`**

## **Docstring:**
```
Retrieves a mapping of tempo settings for the network.

Queries the network to obtain the tempo (rate of reward distributions)
settings for various network subnets.

Returns:
    A dictionary mapping network UIDs to their tempo settings.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_immunity_period`**

## **Docstring:**
```
Retrieves a mapping of immunity periods for the network.

Queries the network for the immunity period settings,
which represent the time duration during which modules
can not get deregistered.

Returns:
    A dictionary mapping network UIDs to their immunity period settings.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_min_allowed_weights`**

## **Docstring:**
```
Retrieves a mapping of minimum allowed weights for the network.

Queries the network to obtain the minimum allowed weights,
which are the lowest permissible weight values that can be set by
validators.

Returns:
    A dictionary mapping network UIDs to
    their minimum allowed weight values.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_max_allowed_weights`**

## **Docstring:**
```
Retrieves a mapping of maximum allowed weights for the network.

Queries the network for the maximum allowed weights,
which are the highest permissible
weight values that can be set by validators.

Returns:
    A dictionary mapping network UIDs to
    their maximum allowed weight values.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_max_allowed_uids`**

## **Docstring:**
```
Queries the network for the maximum number of allowed user IDs (UIDs)
for each network subnet.

Fetches a mapping of network subnets to their respective
limits on the number of user IDs that can be created or used.

Returns:
    A dictionary mapping network UIDs (unique identifiers) to their
    maximum allowed number of UIDs.
    Each entry represents a network subnet
    with its corresponding UID limit.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_min_stake`**

## **Docstring:**
```
Retrieves a mapping of minimum allowed stake on the network.

Queries the network to obtain the minimum number of stake,
which is represented in nanotokens.

Returns:
    A dictionary mapping network UIDs to
    their minimum allowed stake values.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_max_stake`**

## **Docstring:**
```
Retrieves a mapping of the maximum stake values for the network.

Queries the network for the maximum stake values across various s
ubnets of the network.

Returns:
    A dictionary mapping network UIDs to their maximum stake values.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_founder`**

## **Docstring:**
```
Retrieves a mapping of founders for the network.

Queries the network to obtain the founders associated with
various subnets.

Returns:
    A dictionary mapping network UIDs to their respective founders.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, str]`

---

**`query_map_founder_share`**

## **Docstring:**
```
Retrieves a mapping of founder shares for the network.

Queries the network for the share percentages
allocated to founders across different subnets.

Returns:
    A dictionary mapping network UIDs to their founder share percentages.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_incentive_ratio`**

## **Docstring:**
```
Retrieves a mapping of incentive ratios for the network.

Queries the network for the incentive ratios,
which are the proportions of rewards or incentives
allocated in different subnets of the network.

Returns:
    A dictionary mapping network UIDs to their incentive ratios.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_trust_ratio`**

## **Docstring:**
```
Retrieves a mapping of trust ratios for the network.

Queries the network for trust ratios,
indicative of the level of trust or credibility assigned
to different subnets of the network.

Returns:
    A dictionary mapping network UIDs to their trust ratios.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_vote_mode_subnet`**

## **Docstring:**
```
Retrieves a mapping of vote modes for subnets within the network.

Queries the network for the voting modes used in different
subnets, which define the methodology or approach of voting within those
subnets.

Returns:
    A dictionary mapping network UIDs to their vote
    modes for subnets.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, str]`

---

**`query_map_legit_whitelist`**

## **Docstring:**
```
Retrieves a mapping of whitelisted addresses for the network.

Queries the network for a mapping of whitelisted addresses
and their respective legitimacy status.

Returns:
    A dictionary mapping addresses to their legitimacy status.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[Ss58Address, int]`

---

**`query_map_subnet_names`**

## **Docstring:**
```
Retrieves a mapping of subnet names within the network.

Queries the network for the names of various subnets,
providing an overview of the different
subnets within the network.

Returns:
    A dictionary mapping network UIDs to their subnet names.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[int, str]`

---

**`query_map_balances`**

## **Docstring:**
```
Retrieves a mapping of account balances within the network.

Queries the network for the balances associated with different accounts.
It provides detailed information including various types of
balances for each account.

Returns:
    A dictionary mapping account addresses to their balance details.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `extract_value`: `bool`

## **Returns:** `dict[str, dict['str', int | dict[str, int]]]`

---

**`query_map_registration_blocks`**

## **Docstring:**
```
Retrieves a mapping of registration blocks for UIDs on the network.

Queries the network to find the block numbers at which various
UIDs were registered.

Args:
    netuid: The network UID from which to get the registrations.

Returns:
    A dictionary mapping UIDs to their registration block numbers.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[int, int]`

---

**`query_map_name`**

## **Docstring:**
```
Retrieves a mapping of names for keys on the network.

Queries the network for the names associated with different keys.
It provides a mapping of key UIDs to their registered names.

Args:
    netuid: The network UID from which to get the names.

Returns:
    A dictionary mapping key UIDs to their names.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`
- `extract_value`: `bool`

## **Returns:** `dict[int, str]`

---

**`get_immunity_period`**

## **Docstring:**
```
Queries the network for the immunity period setting.

The immunity period is a time duration during which a module
can not be deregistered from the network.
Fetches the immunity period for a specified network subnet.

Args:
    netuid: The network UID for which to query the immunity period.

Returns:
    The immunity period setting for the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_max_set_weights_per_epoch`**

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`get_min_allowed_weights`**

## **Docstring:**
```
Queries the network for the minimum allowed weights setting.

Retrieves the minimum weight values that are possible to set
by a validator within a specific network subnet.

Args:
    netuid: The network UID for which to query the minimum allowed
      weights.

Returns:
    The minimum allowed weight values for the specified network
      subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_dao_treasury_address`**

## **Parameters:**
- `self`

## **Returns:** `Ss58Address`

---

**`get_max_allowed_weights`**

## **Docstring:**
```
Queries the network for the maximum allowed weights setting.

Retrieves the maximum weight values that are possible to set
by a validator within a specific network subnet.

Args:
    netuid: The network UID for which to query the maximum allowed
      weights.

Returns:
    The maximum allowed weight values for the specified network
      subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_max_allowed_uids`**

## **Docstring:**
```
Queries the network for the maximum allowed UIDs setting.

Fetches the upper limit on the number of user IDs that can
be allocated or used within a specific network subnet.

Args:
    netuid: The network UID for which to query the maximum allowed UIDs.

Returns:
    The maximum number of allowed UIDs for the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_name`**

## **Docstring:**
```
Queries the network for the name of a specific subnet.

Args:
    netuid: The network UID for which to query the name.

Returns:
    The name of the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `str`

---

**`get_subnet_name`**

## **Docstring:**
```
Queries the network for the name of a specific subnet.

Args:
    netuid: The network UID for which to query the name.

Returns:
    The name of the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `str`

---

**`get_global_dao_treasury`**

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`get_n`**

## **Docstring:**
```
Queries the network for the 'N' hyperparameter, which represents how
many modules are on the network.

Args:
    netuid: The network UID for which to query the 'N' hyperparameter.

Returns:
    The value of the 'N' hyperparameter for the specified network
      subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_tempo`**

## **Docstring:**
```
Queries the network for the tempo setting, measured in blocks, for the
specified subnet.

Args:
    netuid: The network UID for which to query the tempo.

Returns:
    The tempo setting for the specified subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_total_stake`**

## **Docstring:**
```
Queries the network for the total stake amount.

Retrieves the total amount of stake within a specific network subnet.

Args:
    netuid: The network UID for which to query the total stake.

Returns:
    The total stake amount for the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`get_registrations_per_block`**

## **Docstring:**
```
Queries the network for the number of registrations per block.

Fetches the number of registrations that are processed per
block within the network.

Returns:
    The number of registrations processed per block.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`max_registrations_per_block`**

## **Docstring:**
```
Queries the network for the maximum number of registrations per block.

Retrieves the upper limit of registrations that can be processed in
each block within a specific network subnet.

Args:
    netuid: The network UID for which to query.

Returns:
    The maximum number of registrations per block for
    the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`get_proposal`**

## **Docstring:**
```
Queries the network for a specific proposal.

Args:
    proposal_id: The ID of the proposal to query.

Returns:
    The details of the specified proposal.

Raises:
    QueryError: If the query to the network fails, is invalid,
        or if the proposal ID does not exist.
```

## **Parameters:**
- `self`
- `proposal_id`: `int`

## **Returns:** `None specified`

---

**`get_trust`**

## **Docstring:**
```
Queries the network for the trust setting of a specific network subnet.

Retrieves the trust level or score, which may represent the
level of trustworthiness or reliability within a
particular network subnet.

Args:
    netuid: The network UID for which to query the trust setting.

Returns:
    The trust level or score for the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`get_uids`**

## **Docstring:**
```
Queries the network for module UIDs associated with a specific key.

Args:
    key: The key address for which to query UIDs.
    netuid: The network UID within which to search for the key.

Returns:
    A list of UIDs associated with the specified key.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `key`: `Ss58Address`
- `netuid`: `int`

## **Returns:** `bool | None`

---

**`get_unit_emission`**

## **Docstring:**
```
Queries the network for the unit emission setting.

Retrieves the unit emission value, which represents the
emission rate or quantity for the $COMAI token.

Returns:
    The unit emission value in nanos for the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_tx_rate_limit`**

## **Docstring:**
```
Queries the network for the transaction rate limit.

Retrieves the rate limit for transactions within the network,
which defines the maximum number of transactions that can be
processed within a certain timeframe.

Returns:
    The transaction rate limit for the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_burn_rate`**

## **Docstring:**
```
Queries the network for the burn rate setting.

Retrieves the burn rate, which represents the rate at
which the $COMAI token is permanently
removed or 'burned' from circulation.

Returns:
    The burn rate for the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_burn`**

## **Docstring:**
```
Queries the network for the burn setting.

Retrieves the burn value, which represents the amount of the
$COMAI token that is 'burned' or permanently removed from
circulation.

Args:
    netuid: The network UID for which to query the burn value.

Returns:
    The burn value for the specified network subnet.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_min_burn`**

## **Docstring:**
```
Queries the network for the minimum burn setting.

Retrieves the minimum burn value, indicating the lowest
amount of the $COMAI tokens that can be 'burned' or
permanently removed from circulation.

Returns:
    The minimum burn value for the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_min_weight_stake`**

## **Docstring:**
```
Queries the network for the minimum weight stake setting.

Retrieves the minimum weight stake, which represents the lowest
stake weight that is allowed for certain operations or
transactions within the network.

Returns:
    The minimum weight stake for the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_vote_mode_global`**

## **Docstring:**
```
Queries the network for the global vote mode setting.

Retrieves the global vote mode, which defines the overall voting
methodology or approach used across the network in default.

Returns:
    The global vote mode setting for the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `str`

---

**`get_max_proposals`**

## **Docstring:**
```
Queries the network for the maximum number of proposals allowed.

Retrieves the upper limit on the number of proposals that can be
active or considered at any given time within the network.

Returns:
    The maximum number of proposals allowed on the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_max_registrations_per_block`**

## **Docstring:**
```
Queries the network for the maximum number of registrations per block.

Retrieves the maximum number of registrations that can
be processed in each block within the network.

Returns:
    The maximum number of registrations per block on the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_max_name_length`**

## **Docstring:**
```
Queries the network for the maximum length allowed for names.

Retrieves the maximum character length permitted for names
within the network. Such as the module names

Returns:
    The maximum length allowed for names on the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_global_vote_threshold`**

## **Docstring:**
```
Queries the network for the global vote threshold.

Retrieves the global vote threshold, which is the critical value or
percentage required for decisions in the network's governance process.

Returns:
    The global vote threshold for the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_max_allowed_subnets`**

## **Docstring:**
```
Queries the network for the maximum number of allowed subnets.

Retrieves the upper limit on the number of subnets that can
be created or operated within the network.

Returns:
    The maximum number of allowed subnets on the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_max_allowed_modules`**

## **Docstring:**
```
Queries the network for the maximum number of allowed modules.

Retrieves the upper limit on the number of modules that
can be registered within the network.

Returns:
    The maximum number of allowed modules on the network.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_min_stake`**

## **Docstring:**
```
Queries the network for the minimum stake required to register a key.

Retrieves the minimum amount of stake necessary for
registering a key within a specific network subnet.

Args:
    netuid: The network UID for which to query the minimum stake.

Returns:
    The minimum stake required for key registration in nanos.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_stake`**

## **Docstring:**
```
Queries the network for the stake delegated with a specific key.

Retrieves the amount of total staked tokens
delegated a specific key address

Args:
    key: The address of the key to query the stake for.
    netuid: The network UID from which to get the query.

Returns:
    The amount of stake held by the specified key in nanos.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `key`: `Ss58Address`
- `netuid`: `int`

## **Returns:** `int`

---

**`get_stakefrom`**

## **Docstring:**
```
Retrieves a list of keys from which a specific key address is staked.

Queries the network for all the stakes received by a
particular key from different sources.

Args:
    key_addr: The address of the key to query stakes from.

    netuid: The network UID from which to get the query.

Returns:
    A dictionary mapping key addresses to the amount of stake
    received from each.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `key_addr`: `Ss58Address`
- `netuid`: `int`

## **Returns:** `dict[str, int]`

---

**`get_staketo`**

## **Docstring:**
```
Retrieves a list of keys to which a specific key address stakes to.

Queries the network for all the stakes made by a particular key to
different destinations.

Args:
    key_addr: The address of the key to query stakes to.

    netuid: The network UID from which to get the query.

Returns:
    A dictionary mapping key addresses to the
    amount of stake given to each.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `key_addr`: `Ss58Address`
- `netuid`: `int`

## **Returns:** `dict[str, int]`

---

**`get_balance`**

## **Docstring:**
```
Retrieves the balance of a specific key.

Args:
    addr: The address of the key to query the balance for.

Returns:
    The balance of the specified key.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `addr`: `Ss58Address`

## **Returns:** `int`

---

**`get_block`**

## **Docstring:**
```
Retrieves information about a specific block in the network.

Queries the network for details about a block, such as its number,
hash, and other relevant information.

Returns:
    The requested information about the block,
    or None if the block does not exist
    or the information is not available.

Raises:
    QueryError: If the query to the network fails or is invalid.
```

## **Parameters:**
- `self`
- `block_hash`: `str | None`

## **Returns:** `dict[Any, Any] | None`

---

**`get_existential_deposit`**

## **Docstring:**
```
Retrieves the existential deposit value for the network.

The existential deposit is the minimum balance that must be maintained
in an account to prevent it from being purged. Denotated in nano units.

Returns:
    The existential deposit value in nano units.
Note:
    The value returned is a fixed value defined in the
    client and may not reflect changes in the network's configuration.
```

## **Parameters:**
- `self`
- `block_hash`: `str | None`

## **Returns:** `int`

---

**`get_voting_power_delegators`**

## **Parameters:**
- `self`

## **Returns:** `list[Ss58Address]`

---

**`add_transfer_dao_treasury_proposal`**

## **Parameters:**
- `self`
- `key`: `Keypair`
- `data`: `str`
- `amount_nano`: `int`
- `dest`: `Ss58Address`

## **Returns:** `None specified`

---

**`estimate_size`**

## **Docstring:**
```
Convert the batch request to a string and measure its length
```

## **Parameters:**
- `request`: `tuple[T1, T2]`

## **Returns:** `None specified`

---

**`split_chunks`**

## **Parameters:**
- `chunk`: `Chunk`
- `chunk_info`: `list[Chunk]`
- `chunk_info_idx`: `int`

## **Returns:** `None specified`

---

**`concat_hash_len`**

## **Docstring:**
```
Determines the length of the hash based on the given key hasher type.

Args:
    key_hasher: The type of key hasher.

Returns:
    The length of the hash corresponding to the given key hasher type.

Raises:
    ValueError: If the key hasher type is not supported.

Example:
    >>> concat_hash_len("Blake2_128Concat")
    16
```

## **Parameters:**
- `key_hasher`: `str`

## **Returns:** `int`

---

**`recursive_update`**

## **Parameters:**
- `d`: `dict[str, dict[T1, T2] | dict[str, Any]]`
- `u`: `Mapping[str, dict[Any, Any] | str]`

## **Returns:** `dict[str, dict[T1, T2]]`

---

**`get_page`**

## **Parameters:**
None

## **Returns:** `None specified`

---

**`get_map_modules`**

## **Docstring:**
```
Gets all modules info on the network
```

## **Parameters:**
- `client`: `CommuneClient`
- `netuid`: `int`
- `include_balances`: `bool`

## **Returns:** `dict[str, ModuleInfoWithOptionalBalance]`

---

**`to_snake_case`**

## **Docstring:**
```
Converts a dictionary with camelCase keys to snake_case keys
```

## **Parameters:**
- `d`: `dict[str, T]`

## **Returns:** `dict[str, T]`

---

**`get_map_subnets_params`**

## **Docstring:**
```
Gets all subnets info on the network
```

## **Parameters:**
- `client`: `CommuneClient`
- `block_hash`: `str | None`

## **Returns:** `dict[int, SubnetParamsWithEmission]`

---

**`get_global_params`**

## **Docstring:**
```
Returns global parameters of the whole commune ecosystem
```

## **Parameters:**
- `c_client`: `CommuneClient`

## **Returns:** `NetworkParams`

---

**`concat_to_local_keys`**

## **Parameters:**
- `balance`: `dict[str, int]`
- `local_key_info`: `dict[str, Ss58Address]`

## **Returns:** `dict[str, int]`

---

**`local_keys_to_freebalance`**

## **Parameters:**
- `c_client`: `CommuneClient`
- `local_keys`: `dict[str, Ss58Address]`

## **Returns:** `dict[str, int]`

---

**`local_keys_to_stakedbalance`**

## **Parameters:**
- `netuid`: `list[int]`

## **Returns:** `dict[str, int]`

---

**`local_keys_allbalance`**

## **Parameters:**
- `c_client`: `CommuneClient`
- `local_keys`: `dict[str, Ss58Address]`
- `netuid`: `int | None`

## **Returns:** `tuple[dict[str, int], dict[str, int]]`

---

**`snakerize`**

## **Parameters:**
- `camel`: `str`

## **Returns:** `str`

---

**`show`**

## **Docstring:**
```
Show information about a key.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `show_private`: `bool`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`free_balance`**

## **Docstring:**
```
Gets free balance of a key.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `unit`: `BalanceUnit`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`staked_balance`**

## **Docstring:**
```
Gets the balance staked on the key itself.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `netuid`: `int`
- `unit`: `BalanceUnit`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`all_balance`**

## **Docstring:**
```
Gets entire balance of a key (free balance + staked balance).
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `netuid`: `int`
- `unit`: `BalanceUnit`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`get_staked`**

## **Docstring:**
```
Gets total stake of a key it delegated across other keys.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `netuid`: `int`
- `unit`: `BalanceUnit`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`run_faucet`**

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `num_processes`: `Optional[int]`
- `num_executions`: `int`

## **Returns:** `None specified`

---

**`transfer_dao_funds`**

## **Parameters:**
- `ctx`: `Context`
- `signer_key`: `str`
- `amount`: `float`
- `cid_hash`: `str`
- `dest`: `str`

## **Returns:** `None specified`

---

**`last_block`**

## **Docstring:**
```
Gets the last block
```

## **Parameters:**
- `ctx`: `Context`
- `hash`: `bool`

## **Returns:** `None specified`

---

**`params`**

## **Docstring:**
```
Gets global params
```

## **Parameters:**
- `ctx`: `Context`

## **Returns:** `None specified`

---

**`list_proposals`**

## **Docstring:**
```
Gets proposals
```

## **Parameters:**
- `ctx`: `Context`
- `query_cid`: `bool`

## **Returns:** `None specified`

---

**`propose_globally`**

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `cid`: `str`
- `max_allowed_modules`: `int`
- `max_registrations_per_block`: `int`
- `max_name_length`: `int`
- `min_name_length`: `int`
- `min_burn`: `int`
- `max_burn`: `int`
- `min_weight_stake`: `int`
- `max_allowed_subnets`: `int`
- `curator`: `str`
- `proposal_cost`: `int`
- `proposal_expiration`: `int`
- `subnet_stake_threshold`: `int`
- `general_subnet_application_cost`: `int`
- `floor_founder_share`: `int`
- `floor_delegation_fee`: `int`
- `max_allowed_weights`: `int`

## **Returns:** `None specified`

---

**`get_valid_voting_keys`**

## **Parameters:**
- `ctx`: `CustomCtx`
- `client`: `CommuneClient`
- `proposal`: `dict[str, Any]`

## **Returns:** `dict[str, int]`

---

**`vote_proposal`**

## **Docstring:**
```
Casts a vote on a specified proposal. Without specifying a key, all keys on disk will be used.
```

## **Parameters:**
- `ctx`: `Context`
- `proposal_id`: `int`
- `key`: `Optional[str]`
- `agree`: `bool`

## **Returns:** `None specified`

---

**`unvote_proposal`**

## **Docstring:**
```
Retracts a previously cast vote on a specified proposal.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `proposal_id`: `int`

## **Returns:** `None specified`

---

**`registration_burn`**

## **Docstring:**
```
Appraises the cost of registering a module on the Commune network.
```

## **Parameters:**
- `ctx`: `Context`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`list_to_ss58`**

## **Docstring:**
```
Raises AssertionError if some input is not a valid Ss58Address.
```

## **Parameters:**
- `str_list`: `list[str] | None`

## **Returns:** `list[Ss58Address] | None`

---

**`register`**

## **Docstring:**
```
Registers a module on the Commune network.
```

## **Parameters:**
- `ctx`: `Context`
- `name`: `str`
- `key`: `str`
- `ip`: `Optional[str]`
- `port`: `Optional[int]`
- `netuid`: `Optional[int]`
- `stake`: `Optional[float]`
- `metadata`: `Optional[str]`
- `new_subnet_name`: `Optional[str]`

## **Returns:** `None specified`

---

**`update`**

## **Docstring:**
```
Updates a subnet.
```

## **Parameters:**
- `ctx`: `Context`
- `netuid`: `int`
- `key`: `str`
- `founder`: `str`
- `founder_share`: `int`
- `immunity_period`: `int`
- `incentive_ratio`: `int`
- `max_allowed_uids`: `int`
- `max_allowed_weights`: `int`
- `min_allowed_weights`: `int`
- `max_weight_age`: `int`
- `min_stake`: `int`
- `name`: `str`
- `tempo`: `int`
- `trust_ratio`: `int`
- `bonds_ma`: `int`
- `maximum_set_weight_calls_per_epoch`: `int`
- `target_registrations_per_interval`: `int`
- `target_registrations_interval`: `int`
- `max_registrations_per_interval`: `int`
- `vote_mode`: `str`
- `adjustment_alpha`: `int`

## **Returns:** `None specified`

---

**`serve`**

## **Docstring:**
```
Serves a module on `127.0.0.1` on port `port`. `class_path` should specify
the dotted path to the module class e.g. `module.submodule.ClassName`.
```

## **Parameters:**
- `ctx`: `typer.Context`
- `class_path`: `str`
- `key`: `str`
- `port`: `int`
- `ip`: `Optional[str]`
- `subnets_whitelist`: `Optional[list[int]]`
- `whitelist`: `Optional[list[str]]`
- `blacklist`: `Optional[list[str]]`
- `ip_blacklist`: `Optional[list[str]]`
- `test_mode`: `Optional[bool]`
- `request_staleness`: `int`
- `use_ip_limiter`: `Optional[bool]`
- `token_refill_rate_base_multiplier`: `Optional[int]`

## **Returns:** `None specified`

---

**`info`**

## **Parameters:**
- `self`
- `message`: `str`

## **Returns:** `None specified`

---

**`inventory`**

## **Docstring:**
```
Lists all keys stored on disk.
```

## **Parameters:**
- `ctx`: `Context`
- `use_universal_password`: `bool`

## **Returns:** `None specified`

---

**`main`**

## **Parameters:**
- `client`: `CommuneClient`
- `key`: `Keypair`

## **Returns:** `None specified`

---

**`list`**

## **Docstring:**
```
Gets subnets.
```

## **Parameters:**
- `ctx`: `Context`

## **Returns:** `None specified`

---

**`legit_whitelist`**

## **Docstring:**
```
Gets the legitimate whitelist of modules for the general subnet 0
```

## **Parameters:**
- `ctx`: `Context`

## **Returns:** `None specified`

---

**`propose_on_subnet`**

## **Docstring:**
```
Adds a proposal to a specific subnet.
```

## **Parameters:**
- `ctx`: `Context`
- `netuid`: `int`
- `key`: `str`
- `cid`: `str`
- `founder`: `str`
- `founder_share`: `int`
- `immunity_period`: `int`
- `incentive_ratio`: `int`
- `max_allowed_uids`: `int`
- `max_allowed_weights`: `int`
- `min_allowed_weights`: `int`
- `max_weight_age`: `int`
- `min_stake`: `int`
- `name`: `str`
- `tempo`: `int`
- `trust_ratio`: `int`
- `bonds_ma`: `int`
- `maximum_set_weight_calls_per_epoch`: `int`
- `target_registrations_per_interval`: `int`
- `target_registrations_interval`: `int`
- `max_registrations_per_interval`: `int`
- `vote_mode`: `str`
- `adjustment_alpha`: `int`

## **Returns:** `None specified`

---

**`submit_general_subnet_application`**

## **Docstring:**
```
Submits a legitimate whitelist application to the general subnet, netuid 0.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `application_key`: `str`
- `cid`: `str`

## **Returns:** `None specified`

---

**`list_curator_applications`**

## **Parameters:**
- `ctx`: `Context`

## **Returns:** `None specified`

---

**`make_custom_context`**

## **Parameters:**
- `ctx`: `typer.Context`

## **Returns:** `CustomCtx`

---

**`eprint`**

## **Docstring:**
```
Pretty prints an error.
```

## **Parameters:**
- `e`: `Any`

## **Returns:** `None`

---

**`print_table_from_plain_dict`**

## **Docstring:**
```
Creates a table for a plain dictionary.
```

## **Parameters:**
- `result`: `Mapping[str, str | int | float]`
- `column_names`: `list[str]`
- `console`: `Console`

## **Returns:** `None`

---

**`print_table_standardize`**

## **Docstring:**
```
Creates a table for a standardized dictionary.
```

## **Parameters:**
- `result`: `dict[str, list[Any]]`
- `console`: `Console`

## **Returns:** `None`

---

**`transform_module_into`**

## **Parameters:**
- `to_exclude`: `list[str]`
- `last_block`: `int`
- `immunity_period`: `int`
- `modules`: `list[ModuleInfoWithOptionalBalance]`
- `tempo`: `int`

## **Returns:** `None specified`

---

**`print_module_info`**

## **Docstring:**
```
Prints information about a module.
```

## **Parameters:**
- `client`: `CommuneClient`
- `modules`: `list[ModuleInfoWithOptionalBalance]`
- `console`: `Console`
- `netuid`: `int`
- `title`: `str | None`

## **Returns:** `None`

---

**`get_universal_password`**

## **Parameters:**
- `ctx`: `CustomCtx`

## **Returns:** `str`

---

**`com_client`**

## **Parameters:**
- `self`

## **Returns:** `CommuneClient`

---

**`get_use_testnet`**

## **Parameters:**
- `self`

## **Returns:** `bool`

---

**`output`**

## **Parameters:**
- `self`
- `message`: `str`

## **Returns:** `None`

---

**`error`**

## **Parameters:**
- `self`
- `message`: `str`

## **Returns:** `None`

---

**`progress_status`**

## **Parameters:**
- `self`
- `message`: `str`

## **Returns:** `None specified`

---

**`confirm`**

## **Parameters:**
- `self`
- `message`: `str`

## **Returns:** `bool`

---

**`create`**

## **Docstring:**
```
Generates a new key and stores it on a disk with the given name.
```

## **Parameters:**
- `ctx`: `Context`
- `name`: `str`
- `password`: `str`

## **Returns:** `None specified`

---

**`regen`**

## **Docstring:**
```
Stores the given key on a disk. Works with private key or mnemonic.
```

## **Parameters:**
- `ctx`: `Context`
- `name`: `str`
- `key_input`: `str`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`balances`**

## **Docstring:**
```
Gets balances of all keys.
```

## **Parameters:**
- `ctx`: `Context`
- `netuid`: `Optional[int]`
- `unit`: `BalanceUnit`
- `sort_balance`: `SortBalance`
- `use_universal_password`: `bool`

## **Returns:** `None specified`

---

**`stakefrom`**

## **Docstring:**
```
Gets what keys is key staked from.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `netuid`: `int`
- `unit`: `BalanceUnit`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`staketo`**

## **Docstring:**
```
Gets stake to a key.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `str`
- `netuid`: `int`
- `unit`: `BalanceUnit`
- `password`: `Optional[str]`

## **Returns:** `None specified`

---

**`total_free_balance`**

## **Docstring:**
```
Returns total balance of all keys on a disk
```

## **Parameters:**
- `ctx`: `Context`
- `unit`: `BalanceUnit`
- `use_universal_password`: `Optional[str]`

## **Returns:** `None specified`

---

**`total_staked_balance`**

## **Docstring:**
```
Returns total stake of all keys on a disk
```

## **Parameters:**
- `ctx`: `Context`
- `unit`: `BalanceUnit`
- `netuid`: `int`
- `use_universal_password`: `bool`

## **Returns:** `None specified`

---

**`total_balance`**

## **Docstring:**
```
Returns total tokens of all keys on a disk
```

## **Parameters:**
- `ctx`: `Context`
- `unit`: `BalanceUnit`
- `netuid`: `Optional[int]`
- `use_universal_password`: `bool`

## **Returns:** `None specified`

---

**`power_delegation`**

## **Docstring:**
```
Gets power delegation of a key.
```

## **Parameters:**
- `ctx`: `Context`
- `key`: `Optional[str]`
- `enable`: `bool`
- `use_universal_password`: `bool`

## **Returns:** `None specified`

---

**`_version_callback`**

## **Parameters:**
- `value`: `bool`

## **Returns:** `None specified`

---

**`flag_option`**

## **Parameters:**
- `flag`: `str`
- `flag_envvar`: `str`
- `flag_help`: `str`
- `flag_short`: `str | None`

## **Returns:** `None specified`

---

**`circulating_tokens`**

## **Docstring:**
```
Gets total circulating supply
```

## **Parameters:**
- `c_client`: `CommuneClient`

## **Returns:** `int`

---

**`circulating_supply`**

## **Docstring:**
```
Gets the value of all keys on the network, stake + balances
```

## **Parameters:**
- `ctx`: `Context`
- `unit`: `BalanceUnit`

## **Returns:** `None specified`

---

**`apr`**

## **Docstring:**
```
Gets the current staking APR on validators.
The miner reinvest rate & fee are specified in percentages.
```

## **Parameters:**
- `ctx`: `Context`
- `fee`: `int`

## **Returns:** `None specified`

---

**`stats`**

## **Parameters:**
- `ctx`: `Context`
- `balances`: `bool`
- `netuid`: `int`

## **Returns:** `None specified`

---

**`get_treasury_address`**

## **Parameters:**
- `ctx`: `Context`

## **Returns:** `None specified`

---

**`_terminate_workers_and_wait_for_exit`**

## **Docstring:**
```
Terminates the worker processes and waits for them to exit.

This function is used to gracefully terminate a list of worker processes
and wait for them to exit.

Args:
    workers: A list of multiprocessing.Process instances representing the worker processes.

Returns:
    None
```

## **Parameters:**
- `workers`: `list[multiprocessing.Process]`

## **Returns:** `None`

---

**`unbox_block_info`**

## **Docstring:**
```
Unboxes the block information from the MutexBox.

This function retrieves the block information from the MutexBox in a blocking manner.

Args:
    block_info_box: A MutexBox containing the block information.

Returns:
    A tuple containing the block number, block and key hash bytes, and block hash.
```

## **Parameters:**
- `block_info_box`: `MutexBox[BlockInfo]`

## **Returns:** `None specified`

---

**`_hash_block_with_key`**

## **Docstring:**
```
Hashes the block with the key using Keccak-256 to get 32 bytes.

Args:
    block_bytes: The block bytes to be hashed.
    key_bytes: The key bytes to be hashed with the block.

Returns:
    The 32-byte hash of the block and key.
```

## **Parameters:**
- `block_bytes`: `bytes`
- `key_bytes`: `bytes`

## **Returns:** `bytes`

---

**`_update_curr_block_worker`**

## **Docstring:**
```
Updates the current block information in a separate thread.

This function continuously retrieves the latest block information from the
Commune client and updates the block_info_box with the new block number,
block hash, and block bytes hashed with the key.

Args:
    block_info_box: A MutexBox containing the block information.
    c_client: The CommuneClient instance used to retrieve block information.
    key_bytes: The key bytes to be hashed with the block.
    sleep_time: The time (in seconds) to sleep between block updates.
```

## **Parameters:**
- `block_info_box`: `MutexBox[BlockInfo]`
- `c_client`: `CommuneClient`
- `key_bytes`: `bytes`
- `sleep_time`: `int`

## **Returns:** `None specified`

---

**`_update_curr_block`**

## **Docstring:**
```
Updates the current block information.

This function retrieves the latest block information from the Commune client
and updates the block_info object with the new block number, block hash, and
block bytes hashed with the key.

Args:
    block_info: The BlockInfo object to be updated.
    c_client: The CommuneClient instance used to retrieve block information.
    key_bytes: The key bytes to be hashed with the block.

Returns:
    A tuple containing a boolean indicating if the block information was updated
    and the new block number.
```

## **Parameters:**
- `block_info`: `BlockInfo`
- `c_client`: `CommuneClient`
- `key_bytes`: `bytes`

## **Returns:** `None specified`

---

**`_hex_bytes_to_u8_list`**

## **Docstring:**
```
Converts hex bytes to a list of unsigned 8-bit integers.

Args:
    hex_bytes: The hex bytes to be converted.

Returns:
    A list of unsigned 8-bit integers.
```

## **Parameters:**
- `hex_bytes`: `bytes`

## **Returns:** `None specified`

---

**`_create_seal_hash`**

## **Docstring:**
```
Creates the seal hash using the block and key hash bytes and the nonce.

Args:
    block_and_key_hash_bytes: The hash bytes of the block and key.
    nonce: The nonce value.

Returns:
    The seal hash as bytes.
```

## **Parameters:**
- `block_and_key_hash_bytes`: `bytes`
- `nonce`: `int`

## **Returns:** `bytes`

---

**`_seal_meets_difficulty`**

## **Docstring:**
```
Checks if the seal meets the required difficulty.

Args:
    seal: The seal hash as bytes.

Returns:
    True if the seal meets the difficulty, False otherwise.
```

## **Parameters:**
- `seal`: `bytes`

## **Returns:** `None specified`

---

**`_solve_for_nonce_block`**

## **Docstring:**
```
Tries to solve the proof-of-work for a block of nonces.

This function iterates over a range of nonces and attempts to find a seal
that meets the required difficulty. If a solution is found, it returns a
POWSolution object containing the nonce, block number, seal, and block hash.

Args:
    nonce_start: The starting nonce value.
    nonce_end: The ending nonce value.
    block_and_key_hash_bytes: The hash bytes of the block and key.
    block_number: The block number.
    block_hash: The block hash.

Returns:
    A POWSolution object if a solution is found, None otherwise.
```

## **Parameters:**
- `nonce_start`: `int`
- `nonce_end`: `int`
- `block_and_key_hash_bytes`: `bytes`
- `block_number`: `int`
- `block_hash`: `str`

## **Returns:** `POWSolution | None`

---

**`get_cpu_count`**

## **Docstring:**
```
Gets the number of allowed CPU cores for the current process.

Returns:
    The number of allowed CPU cores.
```

## **Parameters:**
None

## **Returns:** `None specified`

---

**`solve_for_difficulty_fast`**

## **Docstring:**
```
Solves the proof-of-work using multiple processes.

This function creates multiple solver processes to find a solution for the
proof-of-work. It distributes the work among the processes and waits until
a solution is found or all processes have finished.

Args:
    c_client: The CommuneClient instance used to retrieve block information.
    key: The Keypair used for signing.
    num_processes: The number of solver processes to create (default: number of CPU cores).
    update_interval: The interval at which the solvers update their progress (default: 50,000).

Returns:
    A POWSolution object if a solution is found, None otherwise.
```

## **Parameters:**
- `c_client`: `CommuneClient`
- `key`: `Keypair`
- `node_url`: `str`
- `num_processes`: `Optional[int]`
- `update_interval`: `Optional[int]`

## **Returns:** `None specified`

---

**`put`**

## **Parameters:**
- `self`
- `item`: `T`
- `block`: `bool`
- `timeout`: `float | None`

## **Returns:** `None`

---

**`get`**

## **Parameters:**
- `self`
- `block`: `bool`
- `timeout`: `float | None`

## **Returns:** `T | None`

---

**`__getattr__`**

## **Parameters:**
- `self`
- `name`: `str`

## **Returns:** `None specified`

---

**`put_nowait`**

## **Parameters:**
- `self`
- `item`: `T`

## **Returns:** `None specified`

---

**`is_stale`**

## **Docstring:**
```
Returns True if the POW is stale.
This means the block the POW is solved for is within 3 blocks of the current block.
```

## **Parameters:**
- `self`
- `current_block`: `int`

## **Returns:** `bool`

---

**`run`**

## **Docstring:**
```
Main solver logic.

This method runs the solver process, continuously solving for nonce blocks
until the stop event is set.

The solver retrieves block information from the block_info_box, updates the
current block information in a separate thread, and solves for nonce blocks
within a specified range. If a solution is found, it is put into the solution
queue.
```

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`iso_timestamp_now`**

## **Parameters:**
None

## **Returns:** `str`

---

**`log`**

## **Parameters:**
- `msg`: `str`

## **Returns:** `None specified`

---

**`log_reffusal`**

## **Parameters:**
- `key`: `str`
- `reason`: `str`

## **Returns:** `None specified`

---

**`json_error`**

## **Parameters:**
- `code`: `int`
- `message`: `str`

## **Returns:** `None specified`

---

**`try_ss58_decode`**

## **Parameters:**
- `key`: `bytes | str`

## **Returns:** `None specified`

---

**`retry`**

## **Parameters:**
- `max_retries`: `int | None`
- `retry_exceptions`: `list[type]`

## **Returns:** `None specified`

---

**`make_client`**

## **Parameters:**
- `node_url`: `str`

## **Returns:** `None specified`

---

**`decorator`**

## **Parameters:**
- `func`: `Callable[P, R]`

## **Returns:** `Callable[P, R]`

---

**`wrapper`**

## **Parameters:**
None

## **Returns:** `None specified`

---

**`_build_routers`**

## **Parameters:**
- `self`
- `use_testnet`: `bool`
- `limiter`: `StakeLimiterParams | IpLimiterParams`

## **Returns:** `None specified`

---

**`get_fastapi_app`**

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`register_endpoints`**

## **Parameters:**
- `self`
- `router`: `APIRouter`

## **Returns:** `None specified`

---

**`add_to_blacklist`**

## **Parameters:**
- `self`
- `ss58_address`: `Ss58Address`

## **Returns:** `None specified`

---

**`add_to_whitelist`**

## **Parameters:**
- `self`
- `ss58_address`: `Ss58Address`

## **Returns:** `None specified`

---

**`do_the_thing`**

## **Parameters:**
- `self`
- `awesomness`: `int`

## **Returns:** `None specified`

---

**`handler`**

## **Parameters:**
- `end_def`: `EndpointDefinition[Any, ...]`
- `body`: `Body`

## **Returns:** `None specified`

---

**`sign`**

## **Parameters:**
- `keypair`: `Keypair`
- `data`: `bytes`

## **Returns:** `bytes`

---

**`verify`**

## **Parameters:**
- `pubkey`: `bytes`
- `crypto_type`: `int`
- `data`: `bytes`
- `signature`: `bytes`

## **Returns:** `bool`

---

**`sign_with_metadate`**

## **Docstring:**
```
DEPRECATED
```

## **Parameters:**
- `keypair`: `Keypair`
- `data`: `bytes`

## **Returns:** `None specified`

---

**`endpoint`**

## **Parameters:**
- `fn`: `Callable[P, T]`

## **Returns:** `Callable[P, T]`

---

**`function_params_to_model`**

## **Parameters:**
- `signature`: `inspect.Signature`

## **Returns:** `type[EndpointParams]`

---

**`get_endpoints`**

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`extract_endpoints`**

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`serialize`**

## **Parameters:**
- `data`: `Any`

## **Returns:** `bytes`

---

**`create_headers`**

## **Parameters:**
- `signature`: `bytes`
- `my_key`: `Keypair`
- `timestamp_iso`: `str`

## **Returns:** `None specified`

---

**`create_request_data`**

## **Parameters:**
- `my_key`: `Keypair`
- `target_key`: `Ss58Address`
- `params`: `Any`

## **Returns:** `tuple[bytes, dict[str, str]]`

---

**`create_method_endpoint`**

## **Parameters:**
- `host`: `str`
- `port`: `str | int`
- `method_name`: `str`

## **Returns:** `str`

---

**`prompt`**

## **Parameters:**
- `self`
- `text`: `str`
- `model`: `OpenAIModels`

## **Returns:** `None specified`

---

**`generate`**

## **Parameters:**
None

## **Returns:** `None specified`

---

**`calls_per_epoch`**

## **Docstring:**
```
Gives how many requests per epoch a stake can make
```

## **Parameters:**
- `stake`: `int`
- `multiplier`: `int`

## **Returns:** `float`

---

**`build_keys_refill_rate`**

## **Parameters:**
- `netuid`: `list[int] | None`
- `get_refill_rate`: `Callable[[int], float]`

## **Returns:** `None specified`

---

**`mult_2`**

## **Parameters:**
- `x`: `int`

## **Returns:** `int`

---

**`limit`**

## **Parameters:**
- `self`
- `key`: `str`

## **Returns:** `int`

---

**`_set_tokens`**

## **Parameters:**
- `self`
- `key`: `str`
- `tokens`: `float`

## **Returns:** `None`

---

**`is_hex_string`**

## **Parameters:**
- `string`: `str`

## **Returns:** `None specified`

---

**`parse_hex`**

## **Parameters:**
- `hex_str`: `str`

## **Returns:** `bytes`

---

**`build_route_class`**

## **Parameters:**
- `verifiers`: `Sequence[AbstractVerifier]`

## **Returns:** `type[APIRoute]`

---

**`_check_inputs`**

## **Parameters:**
- `self`
- `request`: `Request`
- `body`: `bytes`
- `module_key`: `Ss58Address`

## **Returns:** `None specified`

---

**`_get_headers_dict`**

## **Parameters:**
- `self`
- `headers`: `starlette.datastructures.Headers`
- `required`: `list[str]`
- `optional`: `list[str]`

## **Returns:** `None specified`

---

**`_check_signature`**

## **Parameters:**
- `self`
- `headers_dict`: `dict[str, str]`
- `body`: `bytes`
- `module_key`: `Ss58Address`

## **Returns:** `None specified`

---

**`_check_key_registered`**

## **Parameters:**
- `self`
- `subnets_whitelist`: `list[int] | None`
- `headers_dict`: `dict[str, str]`
- `blockchain_cache`: `TTLDict[str, list[Ss58Address]]`
- `host_key`: `Keypair`
- `use_testnet`: `bool`

## **Returns:** `None specified`

---

**`get_route_handler`**

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`query_keys`**

## **Parameters:**
- `subnet`: `int`

## **Returns:** `None specified`

---

**`keys_to_uids`**

## **Parameters:**
- `keys`: `dict[int, Ss58Address]`
- `target_keys`: `list[Ss58Address]`

## **Returns:** `list[int]`

---

**`validaiton`**

## **Parameters:**
- `client`: `CommuneClient`
- `key`: `Keypair`

## **Returns:** `None specified`

---

**`check_str`**

## **Parameters:**
- `x`: `Any`

## **Returns:** `str`

---

**`ensure_dir_exists`**

## **Parameters:**
- `path`: `str`

## **Returns:** `None`

---

**`ensure_parent_dir_exists`**

## **Parameters:**
- `path`: `str`

## **Returns:** `None`

---

**`bytes_to_hex`**

## **Docstring:**
```
Converts a string or bytes object to its hexadecimal representation.

If the input is already a string, it assumes that the string is already in
hexadecimal format and returns it as is. If the input is bytes, it converts
the bytes to their hexadecimal string representation.

Args:
    x: The input string or bytes object to be converted to hexadecimal.

Returns:
    The hexadecimal representation of the input.

Examples:
    _to_hex(b'hello') returns '68656c6c6f'
    _to_hex('68656c6c6f') returns '68656c6c6f'
```

## **Parameters:**
- `value`: `str | bytes`

## **Returns:** `str`

---

**`is_ip_valid`**

## **Docstring:**
```
Checks if an ip address is valid
```

## **Parameters:**
- `ip`: `str`

## **Returns:** `bool`

---

**`create_state_fn`**

## **Docstring:**
```
Creates a state function that can be used to get or set a value.
```

## **Parameters:**
- `default`: `Callable[..., T]`

## **Returns:** `SetterGetterFn[T]`

---

**`get_json_from_cid`**

## **Parameters:**
- `cid`: `str`

## **Returns:** `dict[Any, Any] | None`

---

**`convert_cid_on_proposal`**

## **Parameters:**
- `proposals`: `dict[int, dict[str, Any]]`

## **Returns:** `None specified`

---

**`__call__`**

## **Parameters:**
None

## **Returns:** `T`

---

**`state_function`**

## **Parameters:**
- `input`: `Optional[T]`

## **Returns:** `None specified`

---

**`__test`**

## **Parameters:**
None

## **Returns:** `None specified`

---

**`ttl_in_ns`**

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`__repr__`**

## **Parameters:**
- `self`

## **Returns:** `str`

---

**`__is_expired`**

## **Parameters:**
- `self`
- `key`: `K`

## **Returns:** `bool`

---

**`__remove_if_expired`**

## **Parameters:**
- `self`
- `key`: `K`

## **Returns:** `bool`

---

**`clean`**

## **Parameters:**
- `self`

## **Returns:** `None specified`

---

**`__setitem__`**

## **Parameters:**
- `self`
- `key`: `K`
- `value`: `V`

## **Returns:** `None specified`

---

**`__getitem__`**

## **Parameters:**
- `self`
- `key`: `K`

## **Returns:** `V`

---

**`__delitem__`**

## **Parameters:**
- `self`
- `key`: `K`

## **Returns:** `None specified`

---

**`__iter__`**

## **Parameters:**
- `self`

## **Returns:** `Iterator[K]`

---

**`__len__`**

## **Docstring:**
```
Warning: this triggers a cleanup, and is O(n) in the number of items in
the dict.
```

## **Parameters:**
- `self`

## **Returns:** `int`

---

**`get_or_insert_lazy`**

## **Docstring:**
```
Gets the value for the given key, or inserts the value returned by the
given function if the key is not present, returning it.
```

## **Parameters:**
- `self`
- `key`: `K`
- `fn`: `Callable[[], V]`

## **Returns:** `V`

---

**`__enter__`**

## **Parameters:**
- `self`

## **Returns:** `T`

---

**`__exit__`**

## **Parameters:**
- `self`
- `exc_type`: `type[BaseException] | None`
- `exc_value`: `BaseException | None`
- `traceback`: `TracebackType | None`

## **Returns:** `None specified`

---

**`_derive_key`**

## **Parameters:**
- `password`: `str`

## **Returns:** `None specified`

---

**`_encrypt_data`**

## **Parameters:**
- `password`: `str`
- `data`: `Any`

## **Returns:** `str`

---

**`_decrypt_data`**

## **Parameters:**
- `password`: `str`
- `data`: `str`

## **Returns:** `Any`

---

**`classic_load`**

## **Docstring:**
```
Load data from commune data storage.

Args:
    path: Data storage file path.
    mode: Data storage mode.

Returns:
    Data loaded from the data storage.

Todo:
    * Other serialization modes support. Only json mode is supported now.

Raises:
    NotImplementedError: See Todo.
    AssertionError: Raised when the data is not in the classic format.
```

## **Parameters:**
- `path`: `str`
- `mode`: `str`
- `password`: `str | None`

## **Returns:** `Any`

---

**`classic_put`**

## **Docstring:**
```
Put data into commune data storage.

Args:
    path: Data storage path.
    value: Data to store.
    mode: Data storage mode.
    encrypt: Whether to encrypt the data.

Todo:
    * Encryption support.
    * Other serialization modes support. Only json mode is supported now.

Raises:
    NotImplementedError: See Todo.
    TypeError: Raised when value is not a valid type.
    FileExistsError: Raised when the file already exists.
```

## **Parameters:**
- `path`: `str`
- `value`: `Any`
- `mode`: `str`
- `password`: `str | None`

## **Returns:** `None specified`

---

**`check_key_dict`**

## **Docstring:**
```
Validates a given dictionary as a commune key dictionary and returns it.

This function checks if the provided dictionary adheres to the structure of
a CommuneKeyDict, that is used by the classic `commune` library and returns
it if valid.

Args:
    key_dict: The dictionary to validate.

Returns:
    The validated commune key dictionary. Same as input.

Raises:
  AssertionError: If the dictionary does not conform to the expected
    structure.
```

## **Parameters:**
- `key_dict`: `Any`

## **Returns:** `CommuneKeyDict`

---

**`classic_key_path`**

## **Docstring:**
```
Constructs the file path for a key name in the classic commune format.
```

## **Parameters:**
- `name`: `str`

## **Returns:** `str`

---

**`from_classic_dict`**

## **Docstring:**
```
Creates a `Key` from a dict conforming to the classic `commune` format.

Args:
    data: The key data in a classic commune format.
    name: The name to assign to the key.

Returns:
    The reconstructed `Key` instance.

Raises:
    AssertionError: If `data` does not conform to the expected format.
```

## **Parameters:**
- `data`: `dict[Any, Any]`

## **Returns:** `Keypair`

---

**`to_classic_dict`**

## **Docstring:**
```
Converts a keypair to a dictionary conforming to the classic commune format.

Args:
    keypair: The keypair to convert.
    path: The path/name of the key file.
```

## **Parameters:**
- `keypair`: `Keypair`
- `path`: `str`

## **Returns:** `CommuneKeyDict`

---

**`classic_load_key`**

## **Docstring:**
```
Loads the keypair with the given name from a disk.
```

## **Parameters:**
- `name`: `str`
- `password`: `str | None`

## **Returns:** `Keypair`

---

**`is_encrypted`**

## **Docstring:**
```
Checks if the key with the given name is encrypted.
```

## **Parameters:**
- `name`: `str`

## **Returns:** `bool`

---

**`classic_store_key`**

## **Docstring:**
```
Stores the given keypair on a disk under the given name.
```

## **Parameters:**
- `keypair`: `Keypair`
- `name`: `str`
- `password`: `str | None`

## **Returns:** `None`

---

**`try_classic_load_key`**

## **Parameters:**
- `name`: `str`
- `context`: `GenericCtx | None`
- `password`: `str | None`

## **Returns:** `Keypair`

---

**`try_load_key`**

## **Parameters:**
- `name`: `str`
- `context`: `GenericCtx | None`
- `password`: `str | None`

## **Returns:** `None specified`

---

**`local_key_addresses`**

## **Docstring:**
```
Retrieves a mapping of local key names to their SS58 addresses.
If password is passed, it will be used to decrypt every key.
If password is not passed and ctx is,
the user will be prompted for the password.
```

## **Parameters:**
- `ctx`: `GenericCtx | None`
- `universal_password`: `str | None`

## **Returns:** `dict[str, Ss58Address]`

---

**`resolve_key_ss58`**

## **Docstring:**
```
Resolves a keypair or key name to its corresponding SS58 address.

If the input is already an SS58 address, it is returned as is.
```

## **Parameters:**
- `key`: `Ss58Address | Keypair | str`

## **Returns:** `Ss58Address`

---

**`resolve_key_ss58_encrypted`**

## **Docstring:**
```
Resolves a keypair or key name to its corresponding SS58 address.

If the input is already an SS58 address, it is returned as is.
```

## **Parameters:**
- `key`: `Ss58Address | Keypair | str`
- `context`: `GenericCtx`
- `password`: `str | None`

## **Returns:** `Ss58Address`

---

