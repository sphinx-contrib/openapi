.. http:get:: /

   **List API versions**

   :statuscode 200:
      200 response

      .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: application/json

         {
           "versions": [
             {
               "status": "CURRENT",
               "updated": "2011-01-21T11:33:21Z",
               "id": "v2.0",
               "links": [
                 {
                   "href": "http://127.0.0.1:8774/v2/",
                   "rel": "self"
                 }
               ]
             },
             {
               "status": "EXPERIMENTAL",
               "updated": "2013-07-23T11:33:21Z",
               "id": "v3.0",
               "links": [
                 {
                   "href": "http://127.0.0.1:8774/v3/",
                   "rel": "self"
                 }
               ]
             }
           ]
         }
   :statuscode 300:
      300 response

.. http:get:: /v2

   **Show API version details**

   :statuscode 200:
      200 response

      .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: application/json

         {
           "version": {
             "status": "CURRENT",
             "updated": "2011-01-21T11:33:21Z",
             "media-types": [
               {
                 "base": "application/xml",
                 "type": "application/vnd.openstack.compute+xml;version=2"
               },
               {
                 "base": "application/json",
                 "type": "application/vnd.openstack.compute+json;version=2"
               }
             ],
             "id": "v2.0",
             "links": [
               {
                 "href": "http://127.0.0.1:8774/v2/",
                 "rel": "self"
               },
               {
                 "href": "http://docs.openstack.org/api/openstack-compute/2/os-compute-devguide-2.pdf",
                 "type": "application/pdf",
                 "rel": "describedby"
               },
               {
                 "href": "http://docs.openstack.org/api/openstack-compute/2/wadl/os-compute-2.wadl",
                 "type": "application/vnd.sun.wadl+xml",
                 "rel": "describedby"
               },
               {
                 "href": "http://docs.openstack.org/api/openstack-compute/2/wadl/os-compute-2.wadl",
                 "type": "application/vnd.sun.wadl+xml",
                 "rel": "describedby"
               }
             ]
           }
         }
   :statuscode 203:
      203 response
