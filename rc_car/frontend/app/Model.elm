module Model exposing (..)

import Json.Decode
import Json.Encode
--import Json.Decode.Pipeline exposing (decode, required)

type alias Flags =
  { sys_url : String
  }

type DrivingMode
  = Self
  | Record
  | Free

type alias Car =
  { accelerator: Int
  , steering: Int
  , speed: Int
  , driving_mode: DrivingMode
  }

fromStringDrivingMode : String -> Json.Decode.Decoder DrivingMode
fromStringDrivingMode string =
  case string of
    "self" ->
        Json.Decode.succeed Self
    "record" ->
        Json.Decode.succeed Record
    "free" ->
        Json.Decode.succeed Free
    somethingElse ->
        Json.Decode.fail <| "Unknown theme: " ++ somethingElse


decodeDrivingMode : Json.Decode.Decoder DrivingMode
decodeDrivingMode =
  Json.Decode.string
    |> Json.Decode.andThen fromStringDrivingMode

{-encodeDrivingMode : DrivingMode -> Json.Decode.Value
encodeDrivingMode =
  toString >> Json.Encode.string-}

carJsonDecoder =
  Json.Decode.map4 Car
    (Json.Decode.field "accelerator" Json.Decode.int)
    (Json.Decode.field "steering" Json.Decode.int)
    (Json.Decode.field "speed" Json.Decode.int)
    (Json.Decode.field "driving_mode" decodeDrivingMode)

{-carJsonDecoder =
  decode Car
    |> required "accelerator" JsonDecode.int
    |> required "steering" JsonDecode.int
    |> required "speed" JsonDecode.int
-}
type alias Model =
  { flags: Flags
  , car: Car
  }


type alias Error =
  { message: String
  }


init : Flags -> Model
init flags =
  Model flags (Car 0 0 0 Free)
