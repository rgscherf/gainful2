module Main where

import Html exposing (..)
import StartApp
import Effects exposing (Effects)
import Task
import Dict

import Models exposing (..)
import Site exposing (..)
import Update exposing (..)

---------
-- WIRING
---------

app : StartApp.App Model
app = StartApp.start
  { init = init
  , view = view
  , update = update
  , inputs = [ Signal.map (\s -> FromStorage s) localStorageToElm
             , Signal.map InitiateJobsFromJson jsonLocation 
             ]
  }

main : Signal Html
main = app.html

startFilter : Filter
startFilter =
  { allRegions = Dict.empty
  , allOrgs = Dict.empty
  , visibleRegions = []
  , visibleOrgs = []
  }

startModel : Model
startModel =
  { jobs = Nothing
  , jobFilter = startFilter
  , fromStorage = ""
  , showWelcome = True
  }

init : (Model, Effects Action)
init = (startModel, Effects.none)

port tasks : Signal (Task.Task Effects.Never ())
port tasks = app.tasks

port localStorageToElm : Signal String

port jsonLocation : Signal String

port localStorageFromElm : Signal String
port localStorageFromElm = jobsToStorage.signal
