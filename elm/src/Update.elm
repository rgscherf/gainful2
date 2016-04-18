module Update where

import Dict
import Task
import Effects exposing (Effects)
import String
import Set
import Http
import Json.Decode as D exposing ((:=), Decoder)

import Models exposing (..)

update : Action -> Model -> (Model, Effects Action)
update action model =
  case action of
    SortJobs s ->
      ( { model | jobs = sortJobs s model.jobs } , Effects.none)
    NoOp ->
      (model, Effects.none)
    InitiateJobsFromJson str ->
      (model, getJobsFromFile str)
    ShowInitialJobs maybeJobs ->
      let newModel = makeFilter model.jobFilter {model | jobs = maybeJobs}
      in ( {newModel | jobs = sortJobs Organization newModel.jobs } , Effects.none)
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

    Organization ->
      if List.member identifier fil.visibleOrgs
      then { fil | visibleOrgs = List.filter (\x -> x /= identifier) fil.visibleOrgs }
      else { fil | visibleOrgs = identifier :: fil.visibleOrgs }

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
    
jobsToStorage : Signal.Mailbox String
jobsToStorage = Signal.mailbox ""

getJobsFromFile : String -> Effects Action
getJobsFromFile s =
  Http.get decodeJobList s
    |> Task.toMaybe
    |> Task.map ShowInitialJobs
    |> Effects.task

decodeJob : Decoder Job
decodeJob =
    let apply = D.object2 (<|)
        cons = D.succeed
    in
    cons Job
      `apply` ("title" := D.string)
      `apply` ("organization" := D.string)
      `apply` ("division" := D.string)
      `apply` ("url_detail" := D.string)
      `apply` ("date_closing" := D.string)
      `apply` ("salary_waged" := D.bool)
      `apply` ("salary_amount" := D.float)
      `apply` ("region" := D.string)
      `apply` ("date_posted" := D.string)

decodeJobList : Decoder Jobs
decodeJobList = D.list decodeJob
