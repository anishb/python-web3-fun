A playground for python code interacting with blockchains.

### Setup

1. Create a new account at [Alchemy](https://www.alchemy.com/) and setup nodes for both Goerli and Ethereum mainnet.

2. Register for a API Key at [Etherscan](https://etherscan.io/).

3. Generate two private/public key pairs using Metamask. The public key is your wallet address. Here are [instructions](https://metamask.zendesk.com/hc/en-us/articles/360015289632-How-to-export-an-account-s-private-key) for viewing the private key.

4. Visit the [Goerli Faucet](https://goerlifaucet.com/) to drop some test ethereum into each of the wallets.

5. Create a .env file in the root directory and add the following contents.

    ETHEREUM_GOERLI_ENDPOINT='<ALCHEMY GOERLI URL>'
    ETHEREUM_MAINNET_ENDPOINT='<ALCHEMY ETHEREUM URL>'
    ETHERSCAN_API_KEY='<ETHERSCAN API KEY>'
    ACCT1_PRIVATE_KEY='<Private Key 1>'
    ACCT2_PRIVATE_KEY='<Private Key 2>'
