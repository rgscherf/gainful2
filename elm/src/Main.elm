module Main where

import Html exposing (..)
import Http
import StartApp
import Effects exposing (Effects)
import Task
import Json.Decode as D exposing ((:=), Decoder)
import Dict
import Set
import String

import Models exposing (..)
import Site exposing (..)

---------
-- WIRING
---------

app : StartApp.App Model
app = StartApp.start
  { init = init
  , view = view
  , update = update
  , inputs = [Signal.map (\s -> FromStorage s) localStorageToElm]
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
  }

init : (Model, Effects Action)
init = (startModel, getJobs)

port tasks : Signal (Task.Task Effects.Never ())
port tasks = app.tasks

port localStorageToElm : Signal String

port localStorageFromElm : Signal String
port localStorageFromElm = jobsToStorage.signal

jobsToStorage : Signal.Mailbox String
jobsToStorage = Signal.mailbox ""

---------
-- UPDATE
---------

update : Action -> Model -> (Model, Effects Action)
update action model =
  case action of
    SortJobs s ->
      (sortJobs s model, Effects.none)
    NoOp ->
      (model, Effects.none)
    GetJobs ->
      (model, getJobs)
    ShowInitialJobs maybeJobs ->
      let newModel = makeFilter model.jobFilter {model | jobs = maybeJobs}
      in (sortJobs Organization newModel, Effects.none)
    FromStorage str ->
      let newModel = {model | fromStorage = str}
      in ( makeFilter newModel.jobFilter newModel, Effects.none )
    ToggleFilter field identifier ->
      let newModel = { model | jobFilter = toggleFilter field identifier model.jobFilter }
          toLocalStorage = ( Signal.send jobsToStorage.address <| makeString newModel.jobFilter.visibleOrgs )
                      `Task.andThen` (\_ -> Task.succeed NoOp)
                        |> Effects.task
      in (newModel, toLocalStorage)

makeString : List String -> String
makeString l =
  List.intersperse "," l
    |> List.foldl (++) ""

toggleFilter : JobField -> String -> Filter -> Filter
toggleFilter field identifier fil =
  case field of
    Region ->
      -- is region currently visible?
      if List.member identifier fil.visibleRegions
      then
        { fil
          -- make region not visible
          | visibleRegions = List.filter (\x -> x /= identifier) fil.visibleRegions
          -- make all orgs connected to this region not visible
          , visibleOrgs = List.filter
                            (\x -> not <| List.member x
                              (Maybe.withDefault [] <| Dict.get identifier fil.allRegions))
                          fil.visibleOrgs
        }
      else
        { fil
          -- make region active
          | visibleRegions = identifier :: fil.visibleRegions
          -- make all orgs connected to this region active
          , visibleOrgs = Set.toList
                            <| Set.fromList
                            <| (Maybe.withDefault [] <| Dict.get identifier fil.allRegions) ++ fil.visibleOrgs
        }
    Organization ->
      -- is org currently visible?
      if List.member identifier fil.visibleOrgs
      then
        let newFil =
              { fil
                -- make org not visible
                | visibleOrgs = List.filter (\x -> x /= identifier) fil.visibleOrgs
              }
            regionOfOrg i =
              (Maybe.withDefault "" <| Dict.get i newFil.allOrgs)
        in
          { newFil |
          -- if no orgs in this org's region are visible, ensure that region is not visible.
            visibleRegions =
                -- do any orgs in this region appear in the visible list?
                if List.any
                  (\x -> List.member x newFil.visibleOrgs)
                  (Maybe.withDefault []
                    <| Dict.get (regionOfOrg identifier) newFil.allRegions) -- outer .get is the list of orgs in the region

                -- if so, no changes
                then newFil.visibleRegions
                -- if not, filter out the region
                else List.filter (\x -> x /= (regionOfOrg identifier)) newFil.visibleRegions
          }
      else
        { fil
           -- make org visible
          | visibleOrgs = identifier :: fil.visibleOrgs
           -- if all orgs in this org's region are visible, ensure it's visible.
          , visibleRegions =
              -- are all the orgs in this region visible?
              if List.all (\x -> List.member x fil.visibleOrgs) (Maybe.withDefault [] <| Dict.get identifier fil.allRegions)
              -- if so, make sure it's visible
              then
                if List.member (Maybe.withDefault "" <| Dict.get identifier fil.allOrgs) fil.visibleRegions
                then fil.visibleRegions
                else (Maybe.withDefault "" <| Dict.get identifier fil.allOrgs) :: fil.visibleRegions
              -- if not, no changes
              else fil.visibleRegions
        }
    _ -> fil -- we only filter on Region and Organization


makeFilter : Filter -> Model -> Model
makeFilter f m =
  {m | jobFilter = makeEntitiesVisible m.fromStorage <| List.foldr makeSingleEntity f <| Maybe.withDefault [] m.jobs }

makeEntitiesVisible : String -> Filter -> Filter
makeEntitiesVisible str f =
  -- two cases here.
  -- if localstorage is empty (first visit or last transformation was to zero out orgs)
  -- then show all orgs and regions.
  -- else, show orgs from localstorage and their associated regions
  case str of
    "" ->
      { f | visibleOrgs = Dict.keys f.allOrgs
          , visibleRegions = Dict.keys f.allRegions
      }
    a ->
      let ls = String.split "," a
      in
        {f | visibleOrgs = ls
           , visibleRegions = List.map (\x -> Dict.get x f.allOrgs |> Maybe.withDefault "") ls
                                |> Set.fromList
                                |> Set.toList
        }

makeSingleEntity : Job -> Filter -> Filter
makeSingleEntity j f =
  case Dict.get j.region f.allRegions of
    Nothing ->
      { f | allRegions = Dict.insert j.region [j.organization] f.allRegions
          , allOrgs = Dict.insert j.organization j.region f.allOrgs
      }
    Just os ->
      case List.member j.organization os of
        True ->
          f
        False ->
          { f | allOrgs = Dict.insert j.organization j.region f.allOrgs
              , allRegions = Dict.update j.region (\xs -> Just <| j.organization :: (Maybe.withDefault [] xs)) f.allRegions
          }

----------
-- EFFECTS
----------

jobsUrl : String
jobsUrl = "http://localhost:8000/jobs/"

getJobs : Effects Action
getJobs =
  Http.get decodeJobList jobsUrl
    |> Task.toMaybe
    |> Task.map ShowInitialJobs
    |> Effects.task


decodeJob : Decoder Job
decodeJob =
  D.object8 Job
    ("title" := D.string)
    ("organization" := D.string)
    ("division" := D.string)
    ("url_detail" := D.string)
    ("date_closing" := D.string)
    ("salary_waged" := D.bool)
    ("salary_amount" := D.float)
    ("region" := D.string)

decodeJobList : Decoder Jobs
decodeJobList = D.list decodeJob
