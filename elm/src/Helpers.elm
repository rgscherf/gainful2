module Helpers where

elem : a -> List a -> Bool
elem e ls =
  case ls of
    [] -> False
    (x::xs) -> if x == e then True else elem e xs
