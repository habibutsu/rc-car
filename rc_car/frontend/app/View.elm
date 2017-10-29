module View exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)

import String
import Svg
import Svg.Attributes
{-import Svg.Attributes exposing (..)-}

import Subscriptions
import Model exposing(..)

control_buttons : Html Subscriptions.Msg
control_buttons =
  div [class "three wide column"][
    div [class "ui padded grid"][
      div [class "three column row"][
        div [class "column"][],
        div [class "column"][
          button [
              class "ui icon button"
              ,onClick (Subscriptions.ButtonClick "up")][
            i [class "up arrow icon"][]
          ]
        ]
        ,div [class "column"][]
      ],
      div [class "three column row"][
        div [class "column"][
          button [
              class "ui icon button"
              ,onClick (Subscriptions.ButtonClick "left")][
            i [class "left arrow icon"][]
          ]
        ]
        ,div [class "column"][
          button [
              class "ui icon button"
              ,onClick (Subscriptions.ButtonClick "down")][
            i [class "down arrow icon"][]
          ]
        ]
        ,div [class "column"][
          button [
              class "ui icon button"
              ,onClick (Subscriptions.ButtonClick "right")][
            i [class "right arrow icon"][]
          ]
        ]
      ]
    ]
  ]

mode_selector : Model -> Html Subscriptions.Msg
mode_selector model =
  div [class "ui form"]
    [ div [class "grouped fields"]
      [ label[][text "Work mode"]
      , div [class "field"]
        [ div [class "ui toggle checkbox"]
          [ input
            [ type_ "radio"
            , name "mode"
            , checked
                (case model.parameters.mode of
                  Free -> True
                  _ -> False)
            , onClick (Subscriptions.ChangeMode "free")
            ] []
          , label [][text "Free"]
          ]
        ]
      , div [class "field"]
        [ div [class "ui toggle checkbox"]
          [ input
            [ type_ "radio"
            , name "mode"
            , checked
                (case model.parameters.mode of
                  Record -> True
                  _ -> False)
            , onClick (Subscriptions.ChangeMode "record")
            ] []
          , label [][text "Record"]
          ]
        ]
      , div [class "field"]
        [ div [class "ui toggle checkbox"]
          [ input
            [ type_ "radio"
            , name "mode"
            , disabled True
            , checked
                (case model.parameters.mode of
                  Self -> True
                  _ -> False)
            , onClick (Subscriptions.ChangeMode "self")
            ] []
          , label []
            [ text "Self"
            , text (case model.parameters.delay of
                                      Nothing -> " (null)"
                                      Just v -> " (" ++ (toString v) ++ ")"
                                    )]
          ]
        ]
      ]
    ]

view : Model -> Html Subscriptions.Msg
view model =
  let
    {-icon_src = case model.car.driving_mode of
          Self -> "/img/BT_c3angle-128.png"
          Record -> "/img/BT_c3tool-128.png"
          Free -> "/img/BT_c3side-128.png"-}
    icon_src = "/img/BT_c3side-64.png"
  in

  div [class "ui padded grid"] [
    div [class "nine wide column"][
      div [class "ui raised segments"] [
        div [class "ui secondary segment"] [
          text "Video stream"
        ]
        , div [class "ui center aligned segment"] [
          img [src "/video?width=640&height=480"] []
        ]
      ]
    ]
    ,div [class "seven wide column"][
      img [src icon_src] []
      ,div [class "ui raised segments"] [
        div [class "ui secondary segment"] [
          text "Control Panel"
        ]
        ,div [class "ui center aligned segment"] [
          div [class "ui divided list"][
            div [class "item"][
              div [class "left floated header"][
                text "Throttle"
              ]
              ,div [class "right floated header"][
                div [class "ui teal circular big label"][
                    text (toString model.sensors.throttle)
                ]
              ]
            ]
            ,div [class "item"][
              div [class "left floated header"][
                text "Rudder"
              ]
              ,div [class "right floated content"][
                div [class "ui blue circular big label"][
                    text (toString model.sensors.rudder)
                ]
              ]
            ]
            ,div [class "item"][
              div [class "left floated header"][
                text "Radar"
              ]
              ,div [class "right floated content"][
                div [class "ui black circular big label"][
                    text (toString model.sensors.radar)
                ]
              ]
            ]
            ,div [class "item"][
              div [class "left floated header"][
                text "Accelerometer"
              ]
              ,div [class "right floated content"][
                div [class "ui black circular big label"][
                    text (toString
                        (case (List.head model.sensors.accelerometer) of
                          Just v -> v
                          Nothing -> 0))
                ]
                ,div [class "ui black circular big label"][
                    text (toString
                        (case (List.head (List.drop 1 model.sensors.accelerometer)) of
                          Just v -> v
                          Nothing -> 0))
                ]
                ,div [class "ui black circular big label"][
                    text (toString
                        (case (List.head (List.drop 2 model.sensors.accelerometer)) of
                          Just v -> v
                          Nothing -> 0))
                ]
              ]
            ]
            {-,div [class "item"][
              div [class "left floated header"][
                text "Speed"
              ]
              ,div [class "right floated content"][
                div [class "ui violet circular big label"][
                    text (toString model.sensors.speed)
                ]
              ]
            ]-}
          ]
        ]
      ]
    ]
    ,control_buttons
    ,div [class "ten wide column"][
      div [class "ui raised segments", style [("padding", "10px")]] [
        div [class "ui grid"]
          [ div [class "four wide column"]
            [ (mode_selector model)
            ]
          , div [class "four wide column"]
            [ div [class "ui form"]
              [ div
                [ class ("ui field" ++ (
                  case model.parameters.delay of
                    Just v -> ""
                    Nothing -> " error"
                  ))
                ]
                [ label [][text "Simulation delay"]
                , input
                  [ type_ "text"
                  , value
                    (case model.parameters.delay of
                      Just v -> toString v
                      Nothing -> ""
                    )
                  , onInput Subscriptions.ChangeDelay
                  ] []
                ]
              ]
            ]
          , div [class "four wide column"]
            [ div [class "ui form"]
              [ div
                [ class "ui field"]
                [ label [][text "Headlamp"]
                , div [class "ui toggle checkbox"]
                  [ input
                    [ type_ "checkbox"
                    , name "headlamp"
                    , checked
                        (case model.parameters.headlamp of
                          On -> True
                          _ -> False)
                    , onClick (Subscriptions.SwitchHeadlamp)
                    ] []
                  , label [] [text "Headlamp"]
                  ]
                {-, div [class "ui toggle checkbox"]
                  [ input
                    [ type_ "checkbox"
                    , name "headlamp"
                    , checked
                        (case model.parameters.headlamp of
                          On -> True
                          _ -> False)
                    , onClick (Subscriptions.SwitchHeadlamp)
                    ] []
                  ]-}
                ]
              ]
            ]
          ]
        {-Svg.svg [
          Svg.Attributes.viewBox "0 0 100 100",
          Svg.Attributes.width "300px"
        ]
        [
          Svg.circle [
            Svg.Attributes.cx "50",
            Svg.Attributes.cy "50",
            Svg.Attributes.r "50",
            Svg.Attributes.fill "#0B79CE" ] []
          , Svg.line [
            Svg.Attributes.x1 "50",
            Svg.Attributes.y1 "50",
            Svg.Attributes.x2 "50",
            Svg.Attributes.y2 "0",
            Svg.Attributes.stroke "#023963" ] []
        ]-}
      ]
      ,button [
          class "ui icon button"
          ,style [("width", "100%")]
          ,onClick (Subscriptions.ButtonClick "stop")][
        i [class "stop icon"][]
      ]
    ]
    ,control_buttons
  ]


viewMessage : String -> Html msg
viewMessage msg =
  div [] [ text msg ]
