.. http:get:: /products

   **Product Types**

   The Products endpoint returns information about the Uber products offered at a given location. The response includes the display name and other details about each product, and lists the products in the proper display order.

   :queryparam latitude:
      Latitude component of location.
   :queryparamtype latitude: number:double, required
   :queryparam longitude:
      Longitude component of location.
   :queryparamtype longitude: number:double, required
   :resjsonarr product_id:
      Unique identifier representing a specific product for a given latitude & longitude. For example, uberX in San Francisco will have a different product_id than uberX in Los Angeles.
   :resjsonarrtype product_id: string
   :resjsonarr description:
      Description of product.
   :resjsonarrtype description: string
   :resjsonarr display_name:
      Display name of product.
   :resjsonarrtype display_name: string
   :resjsonarr capacity:
      Capacity of product. For example, 4 people.
   :resjsonarrtype capacity: integer
   :resjsonarr image:
      Image URL representing the product.
   :resjsonarrtype image: string

   :statuscode 200:
      An array of products

   :statuscode default:
      Unexpected error

.. http:get:: /estimates/price

   **Price Estimates**

   .. role:: raw-html-m2r(raw)
      :format: html


   The Price Estimates endpoint returns an estimated price range for each product offered at a given location. The price estimate is provided as a formatted string with the full price range and the localized currency symbol.\ :raw-html-m2r:`<br>`\ :raw-html-m2r:`<br>`\ The response also includes low and high estimates, and the `ISO 4217 <http://en.wikipedia.org/wiki/ISO_4217>`_ currency code for situations requiring currency conversion. When surge is active for a particular product, its surge_multiplier will be greater than 1, but the price estimate already factors in this multiplier.

   :queryparam start_latitude:
      Latitude component of start location.
   :queryparamtype start_latitude: number:double, required
   :queryparam start_longitude:
      Longitude component of start location.
   :queryparamtype start_longitude: number:double, required
   :queryparam end_latitude:
      Latitude component of end location.
   :queryparamtype end_latitude: number:double, required
   :queryparam end_longitude:
      Longitude component of end location.
   :queryparamtype end_longitude: number:double, required
   :resjsonarr product_id:
      Unique identifier representing a specific product for a given latitude & longitude. For example, uberX in San Francisco will have a different product_id than uberX in Los Angeles
   :resjsonarrtype product_id: string
   :resjsonarr currency_code:
      `ISO 4217 <http://en.wikipedia.org/wiki/ISO_4217>`_ currency code.
   :resjsonarrtype currency_code: string
   :resjsonarr display_name:
      Display name of product.
   :resjsonarrtype display_name: string
   :resjsonarr estimate:
      Formatted string of estimate in local currency of the start location. Estimate could be a range, a single number (flat rate) or "Metered" for TAXI.
   :resjsonarrtype estimate: string
   :resjsonarr low_estimate:
      Lower bound of the estimated price.
   :resjsonarrtype low_estimate: number
   :resjsonarr high_estimate:
      Upper bound of the estimated price.
   :resjsonarrtype high_estimate: number
   :resjsonarr surge_multiplier:
      Expected surge multiplier. Surge is active if surge_multiplier is greater than 1. Price estimate already factors in the surge multiplier.
   :resjsonarrtype surge_multiplier: number

   :statuscode 200:
      An array of price estimates by product

   :statuscode default:
      Unexpected error

.. http:get:: /estimates/time

   **Time Estimates**

   The Time Estimates endpoint returns ETAs for all products offered at a given location, with the responses expressed as integers in seconds. We recommend that this endpoint be called every minute to provide the most accurate, up-to-date ETAs.

   :queryparam start_latitude:
      Latitude component of start location.
   :queryparamtype start_latitude: number:double, required
   :queryparam start_longitude:
      Longitude component of start location.
   :queryparamtype start_longitude: number:double, required
   :queryparam customer_uuid:
      Unique customer identifier to be used for experience customization.
   :queryparamtype customer_uuid: string:uuid
   :queryparam product_id:
      Unique identifier representing a specific product for a given latitude & longitude.
   :queryparamtype product_id: string
   :resjsonarr product_id:
      Unique identifier representing a specific product for a given latitude & longitude. For example, uberX in San Francisco will have a different product_id than uberX in Los Angeles.
   :resjsonarrtype product_id: string
   :resjsonarr description:
      Description of product.
   :resjsonarrtype description: string
   :resjsonarr display_name:
      Display name of product.
   :resjsonarrtype display_name: string
   :resjsonarr capacity:
      Capacity of product. For example, 4 people.
   :resjsonarrtype capacity: integer
   :resjsonarr image:
      Image URL representing the product.
   :resjsonarrtype image: string

   :statuscode 200:
      An array of products

   :statuscode default:
      Unexpected error

.. http:get:: /me

   **User Profile**

   The User Profile endpoint returns information about the Uber user that has authorized with the application.

   :resjson first_name:
      First name of the Uber user.
   :resjsonobj first_name: string
   :resjson last_name:
      Last name of the Uber user.
   :resjsonobj last_name: string
   :resjson email:
      Email address of the Uber user
   :resjsonobj email: string
   :resjson picture:
      Image URL of the Uber user.
   :resjsonobj picture: string
   :resjson promo_code:
      Promo code of the Uber user.
   :resjsonobj promo_code: string

   :statuscode 200:
      Profile information for a user

   :statuscode default:
      Unexpected error

.. http:get:: /history

   **User Activity**

   .. role:: raw-html-m2r(raw)
      :format: html


   The User Activity endpoint returns data about a user's lifetime activity with Uber. The response will include pickup locations and times, dropoff locations and times, the distance of past requests, and information about which products were requested.\ :raw-html-m2r:`<br>`\ :raw-html-m2r:`<br>`\ The history array in the response will have a maximum length based on the limit parameter. The response value count may exceed limit, therefore subsequent API requests may be necessary.

   :queryparam offset:
      Offset the list of returned results by this amount. Default is zero.
   :queryparamtype offset: integer:int32
   :queryparam limit:
      Number of items to retrieve. Default is 5, maximum is 100.
   :queryparamtype limit: integer:int32
   :resjson offset:
      Position in pagination.
   :resjsonobj offset: integer:int32
   :resjson limit:
      Number of items to retrieve (100 max).
   :resjsonobj limit: integer:int32
   :resjson count:
      Total number of items available.
   :resjsonobj count: integer:int32
   :resjson history[]:
   :resjsonobj history[]: object
   :resjson history[].uuid:
      Unique identifier for the activity
   :resjsonobj history[].uuid: string

   :statuscode 200:
      History information for the given user

   :statuscode default:
      Unexpected error
