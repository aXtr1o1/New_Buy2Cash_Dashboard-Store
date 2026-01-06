from api import recommend_for_product

data = {
  "store_id": "68a2d9b54eba4092ecaf1942",
  "data": [
    {
      "ProductName": "24 Mantra Jaggery Powder 500G                                                                                                                                                                                                                                                                                                                                                                                  ",
      "mrpPrice": 60,
      "offerPrice": 55
    },
    {
      "ProductName": "24 Mantra Moong Dal 500G                                                                                                                                                                                                                                                                                                                                                                                       ",
      "mrpPrice": 180,
      "offerPrice": 165
    },
    {
      "ProductName": "ginger",
      "mrpPrice": 100,
      "offerPrice": 90,
      "posPrice": 100
    },
    {
      "ProductName": "Mango",
      "mrpPrice": 110,
      "offerPrice": 89,
      "posPrice": 100
    },
    {
      "ProductName": "Orange",
      "mrpPrice": 180,
      "offerPrice": 180,
      "posPrice": 180
    }
  ]
}


result = recommend_for_product(data)
print(result)