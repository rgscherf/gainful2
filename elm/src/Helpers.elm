module Helpers where

elem : a -> List a -> Bool
elem e ls = List.foldr (\x acc -> if acc then True else e == x) False ls
