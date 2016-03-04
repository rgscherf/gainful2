module Site where

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Markdown

import Models exposing (..)
import Helpers exposing (elem)

------------
-- MAIN VIEW
------------


view : Signal.Address Action -> Model -> Html
view address model =
  div
    []
    [
      navBar
    , div [class "spacer"] []
    , div [class "filterbox"] <| filterBox address model.jobFilter
    , div [class "spacer"] []
    , viewJobs address model.jobFilter model.jobs
    , div [class "spacer"] []
    , div [class "spacer"] []
    , div [class "spacer"] []
    , div [class "spacer"] []
    , div [] [text <| toString model.jobFilter]
    -- , aboutMessage
    ]

-- NAV

navBar : Html
navBar =
  nav [] [ span [class "logo"] [text "Gainful"]
         , a [href "http://www.google.com"]
             [i [class "fa fa-2x fa-fw fa-info-circle nav-icon"] []]
         , a [href "http://www.github.com/rgscherf/gainful2"]
             [i [class "fa fa-2x fa-fw fa-github nav-icon"] []]
         , a [href "http://www.twitter.com/rgscherf"]
             [i [class "fa fa-2x fa-fw fa-twitter nav-icon"] []]
         ]


-- FILTERBOX

filterBox : Signal.Address Action -> Filter -> List Html
filterBox a f =
  let
      btn field x = button
        [ onClick a (ToggleFilter field <| fst x)
        , class (if snd x then "visible" else "notVisible")
        ]
        [ text <| fst x ]
  in
    [ div [] <|
        [span [] [text "first"]]
        ++ btnsAllNone a Organization f
        ++ (List.map (btn Organization) <| List.sortBy fst f.organizations)
    , div [] <|
        [span [] [text "second"]]
        ++ btnsAllNone a Organization f
        ++ (List.map (btn Organization) <| List.sortBy fst f.organizations)
    ]

btnsAllNone : Signal.Address Action -> SortingCriteria -> Filter -> List Html
btnsAllNone a field f =
  let
    allFieldsVisible field =
      List.all (\x -> x == True)
        <| List.map snd
        <| field f
    anyFieldsVisible field =
      List.any (\x -> x == True)
        <| List.map snd
        <| field f
  in
    [ button [ onClick a (ChangeAllFilter Organization True)
            , class (if allFieldsVisible .organizations then "visible" else "notVisible")
            ]
            [text "Select All"]
    , button [ onClick a (ChangeAllFilter Organization False)
            , class (if anyFieldsVisible .organizations then "notVisible" else "visible")
            ]
            [text "Unselect All"]
    ]


-- Job table

viewJobs : Signal.Address Action -> Filter -> Maybe Jobs -> Html
viewJobs address fil maybeJobs =
  let
      activeOrgs = List.filterMap
                    (\x ->
                      if snd x
                      then Just <| fst x
                      else Nothing)
                    fil.organizations
      jobs = List.filter (\j -> elem j.organization activeOrgs)
              <| Maybe.withDefault [] maybeJobs
      shaded = List.concat <| List.repeat (List.length jobs) [True, False]
      jobAndClass = List.map2 (,) shaded jobs
      tbody = List.concatMap individualJob jobAndClass
  in
    table [align "center"]
      (
        [ tr []
          [
            th [onClick address (SortJobs Organization), class "leftHead"] [text "Organization"]
          , th [onClick address (SortJobs Title), class "leftHead"] [text "Title"]
          , th [onClick address (SortJobs Salary), class "rightHead"] [text "Salary/Wage"]
          , th [onClick address (SortJobs ClosingDate), class "rightHead"] [text "Closing Date"]
          ]
        ]
        ++ tbody
      )

individualJob : (Bool, Job) -> List Html
individualJob (shaded, job) =
  let stringSalary = toString <| if job.salaryWaged then job.salaryAmount else toFloat <| round job.salaryAmount
      postfix = if job.salaryWaged then " /hr" else " /yr"
      orgAndDiv = if job.division /= "" then job.organization ++ ", " ++ job.division else job.organization
      rowClass = if shaded then "shadedRow" else "unshadedRow"
  in
  [tr [class rowClass]
    [
      td [] [text <| orgAndDiv]
    , td [] [a
              [href job.urlDetail]
              [text job.title]
            ]
    , td [align "right"] [text (if job.salaryAmount == 0 then "--" else "$ " ++ stringSalary ++ postfix)]
    , td [align "right"] [text job.dateClosing]
    ]
  ]


-- about page

aboutMessage : Html
aboutMessage = Markdown.toHtml """

# What is Gainful?

Job searching is bad. Government websites are bad. This makes searching for government jobs extra bad.

Gainful makes government job postings simple and sane. Every day, it finds all the newest postings and present them in a table. You can filter and sort listings however you want, and save your results as a daily email newsletter.

No signups, no ads. It could not be easier.

## What job sites does Gainful search?

Glad you asked. Gainful searches the following sources:

- City of Toronto
- City of Victoria
- City of Mississauga
- Ontario Public Service in the GTA (TODO)
- ...etc

## Can I help?

[twitter]: http://www.twitter.com/rgscherf

Yes! [Get in touch][twitter] or make a [pull request](http://www.github.com/rgscherf/gainful2).

## Who wrote Gainful?

Gainful is written by Robert Scherf. He's looking for a job--[hire him][twitter]!

"""
