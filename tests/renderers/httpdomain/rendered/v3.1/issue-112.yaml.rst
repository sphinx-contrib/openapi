.. http:get:: /users

   **Get all users.**

   :queryparam role:
   :resjsonarr id:
      The user ID.
   :resjsonarrtype id: integer
   :resjsonarr username:
      The user name.
   :resjsonarrtype username: string
   :resjsonarr deleted:
      Whether the user account has been deleted.
   :resjsonarrtype deleted: boolean

   :statuscode 200:
      A list of all users.


.. http:get:: /users/{userID}

   **Get a user by ID.**

   :param userID:
   :paramtype userID: string
   :resjson id:
      The user ID.
   :resjsonobj id: integer
   :resjson username:
      The user name.
   :resjsonobj username: string
   :resjson bio:
      A brief bio about the user.
   :resjsonobj bio: string, null
   :resjson deleted:
      Whether the user account has been deleted.
   :resjsonobj deleted: boolean
   :resjson created_at:
      The date the user account was created.
   :resjsonobj created_at: string:date
   :resjson deleted_at:
      The date the user account was deleted.
   :resjsonobj deleted_at: string:date

   :statuscode 200:
      The expected information about a user.

