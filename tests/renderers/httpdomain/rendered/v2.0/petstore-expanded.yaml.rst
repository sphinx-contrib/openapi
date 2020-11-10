.. http:get:: /pets

   Returns all pets from the system that the user has access to

   :queryparam tags:
      tags to filter by
   :queryparamtype tags: array
   :queryparam limit:
      maximum number of results to return
   :queryparamtype limit: integer:int32

   :statuscode 200:
      pet response

   :statuscode default:
      unexpected error

.. http:post:: /pets

   Creates a new pet in the store.  Duplicates are allowed

   :reqjson name:
   :reqjsonobj name: string, required
   :reqjson tag:
   :reqjsonobj tag: string


   :resjson name:
   :resjsonobj name: string
   :resjson tag:
   :resjsonobj tag: string
   :resjson id:
   :resjsonobj id: integer:int64, required

   :statuscode 200:
      pet response

   :statuscode default:
      unexpected error

.. http:get:: /pets/{id}

   Returns a user based on a single ID, if the user does not have access to the pet

   :param id:
      ID of pet to fetch
   :paramtype id: integer:int64, required
   :resjson name:
   :resjsonobj name: string
   :resjson tag:
   :resjsonobj tag: string
   :resjson id:
   :resjsonobj id: integer:int64, required

   :statuscode 200:
      pet response

   :statuscode default:
      unexpected error

.. http:delete:: /pets/{id}

   deletes a single pet based on the ID supplied

   :param id:
      ID of pet to delete
   :paramtype id: integer:int64, required
   :statuscode 204:
      pet deleted
   :statuscode default:
      unexpected error
