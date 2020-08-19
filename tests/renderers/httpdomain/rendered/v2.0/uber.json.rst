.. http:get:: /products

   **Product Types**

   The Products endpoint returns information about the Uber products offered at a given location. The response includes the display name and other details about each product, and lists the products in the proper display order.

   :queryparam latitude:
      Latitude component of location.
   :queryparamtype latitude: number:double, required
   :queryparam longitude:
      Longitude component of location.
   :queryparamtype longitude: number:double, required
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
   :statuscode 200:
      An array of products

   :statuscode default:
      Unexpected error

.. http:get:: /me

   **User Profile**

   The User Profile endpoint returns information about the Uber user that has authorized with the application.

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
   :statuscode 200:
      History information for the given user

   :statuscode default:
      Unexpected error
