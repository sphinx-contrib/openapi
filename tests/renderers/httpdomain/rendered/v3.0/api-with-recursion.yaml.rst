.. http:get:: /

   **List API versions**

   :resjson name:
   :resjsonobj name: string, required
   :resjson children[]:
   :resjsonobj children[]: object

   :statuscode 200:
      200 response

   :statuscode 300:
      300 response

.. http:get:: /v2

   **Show API version details**

   :statuscode 200:
      200 response

   :statuscode 203:
      203 response

   **Response 200** (``application/json``)

   :resjson name:
   :resjsonobj name: string, required
   :resjson children[]:
   :resjsonobj children[]: object

   **Response 203** (``application/json``)

   :resjson name:
   :resjsonobj name: string, required
   :resjson children[]:
   :resjsonobj children[]: object
