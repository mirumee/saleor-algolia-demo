PRODUCT_DATA_FRAGMENT = """
    id
    channelListings {
        id
        channel {
            name
            slug
        }
        isAvailableForPurchase
        isPublished
        pricing {
            onSale
            priceRange {
                start {
                    gross {
                        amount
                        currency
                    }
                }
                stop {
                    gross {
                        amount
                        currency
                    }
                }
            }
        }
    }
    translation(languageCode: $language) {
        name
    }
    slug
    name
    category {
        name
        translation(languageCode: $language) {
            name
        }
        parent {
            name
            translation(languageCode: $language) {
                name
            }
            parent {
                name
                translation(languageCode: $language) {
                    name
                }
                parent {
                    name
                    translation(languageCode: $language) {
                        name
                    }
                }
            }
        }
    }
    collections {
        id
        slug
        name
        backgroundImage {
            url
        }
        translation(languageCode: $language) {
            name
        }
    }
    thumbnail {
        url
        alt
    }
    weight {
        value
        unit
    }
    productType {
        name
    }
    attributes {
        attribute {
        name
        slug
        inputType
        translation(languageCode: $language) {
            name
        }
        }
        values {
        name
        translation(languageCode: $language){
            name
        }
        slug
        boolean
        date
        value
        }
    }
    variants {
        name
        translation(languageCode: $language) {
            name
        }
        quantityAvailable
        weight {
            value
            unit
        }
        attributes {
            attribute {
                name
                slug
                inputType
                translation(languageCode: $language) {
                    name
                }
            }
            values {
                name
                translation(languageCode: $language) {
                    name
                }
                slug
                boolean
                date
                value
            }
        }
    }
"""

FETCH_PRODUCTS_DATA = """
    query fetchProductsData($product_ids: [ID!], $first: Int!, $language: LanguageCodeEnum!, $after: String) {
      products(first: $first, after: $after, filter: { ids: $product_ids }) {
        pageInfo {
            hasNextPage
            endCursor
        }
        edges {
          node {
            %s
          }
        }
      }
    }
    """


FETCH_TOTAL_PRODUCTS = """
    query fetchTotalProducts($after: String) {
      products (after: $after) {
        totalCount
      }
    }
    """

# query fetchProductByIDData($product_id: ID!, $first: Int!, $channel: String!, $language: LanguageCodeEnum!, $after: String) {
FETCH_PRODUCT_BY_ID_DATA = (
    """
    query fetchProductByIDData($product_id: ID!, $language: LanguageCodeEnum!) {
      product(id: $product_id) {
        %s
      }
    }
    """
    % PRODUCT_DATA_FRAGMENT
)


FETCH_LANGUAGES = """
    query {
        shop {
            languages {
                code
                language
            }
        }
    }
"""


FETCH_CHANNELS = """
    query {
        channels {
            name
            slug
        }
    }
"""
