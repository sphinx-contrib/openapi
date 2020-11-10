.. http:get:: /pets

   **List all pets**

   :queryparam limit:
      How many items to return at one time (max 100)
   :queryparamtype limit: integer:int32
   :resjsonarr id:
   :resjsonarrtype id: integer:int64, required
   :resjsonarr name:
   :resjsonarrtype name: string, required
   :resjsonarr tag:
   :resjsonarrtype tag: string

   :statuscode 200:
      A paged array of pets


   :resheader x-next:
      A link to the next page of responses
   :resheadertype x-next: string
   :statuscode default:
      unexpected error

.. http:post:: /pets

   **Create a pet**

   :statuscode 201:
      Null response
   :statuscode default:
      unexpected error

.. http:get:: /pets/{petId}

   **Info for a specific pet**

   :param petId:
      The id of the pet to retrieve
   :paramtype petId: string, required
   :resjsonarr id:
   :resjsonarrtype id: integer:int64, required
   :resjsonarr name:
   :resjsonarrtype name: string, required
   :resjsonarr tag:
   :resjsonarrtype tag: string

   :statuscode 200:
      Expected response to a valid request

   :statuscode default:
      unexpected error
