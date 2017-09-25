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

view : Model -> Html Subscriptions.Msg
view model =
  let
    icon_src = case model.car.driving_mode of
          Self -> "/img/BT_c3angle-128.png"
          Record -> "/img/BT_c3tool-128.png"
          Free -> "/img/BT_c3side-128.png"
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
        , div [class "ui center aligned segment"] [
          div [class "ui divided list"][
            div [class "item"][
              div [class "left floated header"][
                text "Accelerator"
              ]
              ,div [class "right floated header"][
                div [class "ui teal circular big label"][
                    text (toString model.car.accelerator)
                ]
              ]
            ],
            div [class "item"][
              div [class "left floated header"][
                text "Steering"
              ]
              ,div [class "right floated content"][
                div [class "ui blue circular big label"][
                    text (toString model.car.steering)
                ]
              ]
            ],
            div [class "item"][
              div [class "left floated header"][
                text "Speed"
              ]
              ,div [class "right floated content"][
                div [class "ui violet circular big label"][
                    text (toString model.car.speed)
                ]
              ]
            ]
          ]
        ]
      ]
    ]
    ,control_buttons
    ,div [class "ten wide column"][
      div [class "ui raised segments"] [
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
    ]
    ,control_buttons
  ]


viewMessage : String -> Html msg
viewMessage msg =
  div [] [ text msg ]
