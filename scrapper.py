import json
import requests
from bs4 import BeautifulSoup

urls = ["https://phantom.com/learn/guides/how-to-create-a-new-wallet",
        "https://phantom.com/learn/guides/how-to-buy-ethereum-eth-polygon-matic-and-solana-sol",
        "https://phantom.com/learn/guides/how-to-deposit-eth-matic-and-sol-in-my-phantom-wallet",
        "https://phantom.com/learn/guides/how-to-send-tokens-to-an-exchange",
        "https://phantom.com/learn/guides/how-to-interact-and-connect-to-nft-marketplaces",
        "https://phantom.com/learn/blog/phantom-acquires-blowfish",
        "https://phantom.com/learn/blog/base-on-phantom",
        "https://phantom.com/learn/blog/charts-in-phantom",
        "https://phantom.com/learn/crypto-101/bitcoin-guide",
        "https://phantom.com/learn/crypto-101/a-beginner-s-guide-to-solana",
        "https://phantom.com/learn/crypto-101/a-beginner-s-guide-to-ethereum",
        "https://phantom.com/learn/crypto-101/what-is-a-crypto-wallet",
        "https://phantom.com/learn/crypto-101/what-are-stablecoins",
        "https://phantom.com/learn/crypto-101/crypto-bridge",
        "https://phantom.com/learn/crypto-101/common-crypto-scams",
        "https://phantom.com/learn/blog/adopting-sign-in-with-standards",
        "https://phantom.com/learn/blog/keeping-phantom-safe-from-the-demonic-critical-vulnerability",
        "https://phantom.com/learn/blog/introducing-phantom-deeplinks",
        "https://phantom.com/learn/developers/phantom-authentication",
        "https://phantom.com/learn/developers/sign-in-with-solana",
        "https://docs.phantom.app/",
        "https://docs.phantom.app/solana/integrating-phantom",
        "https://docs.phantom.app/solana/detecting-the-provider",
        "https://docs.phantom.app/solana/establishing-a-connection",
        "https://docs.phantom.app/solana/sending-a-transaction",
        "https://docs.phantom.app/solana/sending-a-transaction-1",
        "https://docs.phantom.app/solana/signing-a-message",
        "https://docs.phantom.app/solana/errors",
        "https://docs.phantom.app/bitcoin/integrating-phantom",
        "https://docs.phantom.app/bitcoin/detecting-the-provider",
        "https://docs.phantom.app/bitcoin/establishing-a-connection",
        "https://docs.phantom.app/bitcoin/sending-a-transaction",
        "https://docs.phantom.app/bitcoin/signing-a-message",
        "https://docs.phantom.app/bitcoin/provider-api-reference",
        "https://docs.phantom.app/resources/faq",
        "https://phantom.com/explore/nft-spotlight/BTC-DeGods",
        "https://phantom.com/explore/nft-spotlight/pudgy-penguins",
        "https://phantom.com/explore/nft-spotlight/meegos",
        "https://phantom.com/explore/nft-spotlight/The-Heist",
        "https://phantom.com/explore/nft-spotlight/okay-bears",
        "https://phantom.com/explore/nft-spotlight/okay-bears",
        "https://phantom.com/explore/nft-spotlight/claynosaurz",
        "https://phantom.com/explore/app-spotlight/solana-starter-pack",
        "https://phantom.com/explore/app-spotlight/polymarket-prediction-market",
        "https://phantom.com/explore/app-spotlight/farcaster-warpcast",
        "https://phantom.com/explore/app-spotlight/parcl",
        "https://phantom.com/explore/app-spotlight/star-atlas",
        "https://phantom.com/explore/app-spotlight/drift-protocol",
        "https://phantom.com/explore/app-spotlight/tensor",
        "https://phantom.com/explore/app-spotlight/foundation",
        "https://phantom.com/explore/app-spotlight/trails",
        "https://phantom.com/explore/app-spotlight/sharky",
        "https://phantom.com/explore/app-spotlight/birdeye",
        "https://phantom.com/explore/app-spotlight/floor-nft-app",
        "https://phantom.com/explore/app-spotlight/mint-fun",
        "https://phantom.com/explore/app-spotlight/solarplex",
        "https://phantom.com/learn/developers/jup-airdrop-at-phantom",
        "https://phantom.com/learn/blog/the-complete-guide-to-phantom-deeplinks",
        "https://docs.phantom.app/ethereum-base-and-polygon/detecting-the-provider",
        "https://docs.phantom.app/ethereum-base-and-polygon/establishing-a-connection",
        "https://docs.phantom.app/ethereum-base-and-polygon/sending-a-transaction",
        "https://docs.phantom.app/ethereum-base-and-polygon/signing-a-message",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/properties/isphantom"
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/properties/chainid",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/properties/networkversion",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/properties/selectedaddress",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/properties/_events",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/properties/_eventscount",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/events/connect",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/events/accounts-changed",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/events/disconnect",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/events/chain-changed",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/methods/isconnected",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/methods/request",
        "https://docs.phantom.app/ethereum-base-and-polygon/provider-api-reference/errors",
        "https://docs.phantom.app/phantom-deeplinks/deeplinks-ios-and-android",
        "https://docs.phantom.app/phantom-deeplinks/provider-methods/connect",
        "https://docs.phantom.app/phantom-deeplinks/provider-methods/disconnect",
        "https://docs.phantom.app/phantom-deeplinks/provider-methods/signandsendtransaction",
        "https://docs.phantom.app/phantom-deeplinks/provider-methods/signalltransactions",
        "https://docs.phantom.app/phantom-deeplinks/provider-methods/signtransaction",
        "https://docs.phantom.app/phantom-deeplinks/provider-methods/signmessage",
        "https://docs.phantom.app/phantom-deeplinks/other-methods/browse",
        "https://docs.phantom.app/phantom-deeplinks/other-methods/fungible",
        "https://docs.phantom.app/phantom-deeplinks/other-methods/swap",
        "https://docs.phantom.app/phantom-deeplinks/handling-sessions",
        "https://docs.phantom.app/phantom-deeplinks/specifying-redirects",
        "https://docs.phantom.app/phantom-deeplinks/encryption",
        "https://docs.phantom.app/phantom-deeplinks/limitations",
        "https://docs.phantom.app/library-integrations/dynamic",
        "https://docs.phantom.app/library-integrations/privy",
        "https://docs.phantom.app/library-integrations/rainbowkit",
        "https://docs.phantom.app/library-integrations/wagmi",
        "https://docs.phantom.app/library-integrations/web3-onboard",
        "https://docs.phantom.app/library-integrations/web3-react-v6",
        "https://docs.phantom.app/library-integrations/web3-react-v8",
        "https://docs.phantom.app/developer-powertools/auto-confirm",
        "https://docs.phantom.app/developer-powertools/mobile-web-debugging",
        "https://docs.phantom.app/developer-powertools/blocklist",
        "https://docs.phantom.app/developer-powertools/signing-a-message",
        "https://docs.phantom.app/developer-powertools/solana-priority-fees",
        "https://docs.phantom.app/developer-powertools/solana-token-extensions-token22",
        "https://docs.phantom.app/developer-powertools/solana-versioned-transactions",
        "https://docs.phantom.app/developer-powertools/testnet-mode",
        "https://docs.phantom.app/developer-powertools/wallet-standard",
        "https://docs.phantom.app/best-practices/displaying-apps-within-the-activity-tab",
        "https://docs.phantom.app/best-practices/displaying-your-app",
        "https://docs.phantom.app/best-practices/tokens/home-tab-fungibles",
        "https://docs.phantom.app/best-practices/tokens/collectibles-nfts-and-semi-fungibles",
        "https://docs.phantom.app/best-practices/tokens/supported-media-types",
        "https://docs.phantom.app/resources/sandbox"
        ]

all_data_pairs = []

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract textual content
    main_content = soup.find('main')
    if not main_content:
        continue  # If main_content is not found, skip this URL

    headings = main_content.find_all(['h2', 'h3'])
    data_pairs = []
    for i, heading in enumerate(headings):
        instruction = heading.get_text().strip()
        answer_parts = []
        # Loop through siblings until next heading
        for sibling in heading.next_siblings:
            if sibling.name in ['h2', 'h3']:
                break
            if sibling.name == 'p':
                answer_parts.append(sibling.get_text().strip())
        answer = " ".join(answer_parts)
        if instruction and answer:
            data_pairs.append({"instruction": "Talk about this relating to the wallet Phantom: ", "input": instruction, "output": answer})

    all_data_pairs.extend(data_pairs)
# print(all_data_pairs)

# Write all_data_pairs to a .jsonl file
with open("data.jsonl", "w", encoding="utf-8") as f:
    for dp in all_data_pairs:
        f.write(json.dumps(dp, ensure_ascii=False) + "\n")
