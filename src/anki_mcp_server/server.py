"""
Main server module for Anki-MCP-Server.

This module initializes the FastMCP server and sets up tools
for interacting with Anki-Connect.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from mcp.types import ToolAnnotations
from fastmcp import FastMCP, Context
from pydantic import BaseModel

from .config import config
from .anki_connect_client import AsyncAnkiConnectClient, AnkiConnectError
# Import all Pydantic models from the anki_connect_models_extended immersive
from .model import (
    CardsParam, CardParam, NotesParam, NoteIdParam, DeckNameParam, DeckNamesParam, QueryParam, ModelNameParam,
    GetDecksParams, CreateDeckParams, ChangeDeckParams, DeleteDecksParams, GetDeckConfigParams,
    DeckConfigObject, SaveDeckConfigParams, SetDeckConfigIdParams, CloneDeckConfigIdParams,
    RemoveDeckConfigIdParams, GetDeckStatsParams, GetEaseFactorsParams, SetEaseFactorsParams,
    SetSpecificValueOfCardParams, SuspendCardsParams, UnsuspendCardsParams, SuspendedCardParam,
    AreSuspendedParams, AreDueParams, GetIntervalsParams, FindCardsParams, CardsToNotesParams,
    CardsModTimeParams, CardsInfoParams, ForgetCardsParams, RelearnCardsParams, AnswerCardsParams,
    CardAnswer, SetDueDateParams, NoteMediaAsset, DuplicateScopeOptionsStructure, NoteOptionsStructure,
    NoteToAdd, AddNoteParams, AddNotesParams, NoteToCanAdd, CanAddNotesParams,
    CanAddNotesWithErrorDetailParams, NoteFieldsToUpdate, UpdateNoteFieldsParams, NoteToUpdate,
    UpdateNoteParams, NoteModelToUpdate, UpdateNoteModelParams, UpdateNoteTagsParams, GetNoteTagsParams,
    AddTagsParams, RemoveTagsParams, ReplaceTagsParams, ReplaceTagsInAllNotesParams, FindNotesParams,
    NotesInfoParams, NotesModTimeParamsNotes, DeleteNotesParams, # Deck, Card, Note actions
    GuiBrowseParams, GuiSelectCardParams, GuiAddCardsParams, GuiEditNoteParams, GuiAnswerCardParams,
    GuiDeckOverviewParams, GuiDeckReviewParams, GuiImportFileParams, # Graphical Actions
    StoreMediaFileParams, RetrieveMediaFileParams, GetMediaFilesNamesParams, DeleteMediaFileParams, # Media Actions
    ApiReflectParams, LoadProfileParams, MultiParams, MultiActionItem, ExportPackageParams, ImportPackageParams, # Miscellaneous
    FindModelsByIdParams, FindModelsByNameParams, ModelFieldNamesParams, ModelFieldDescriptionsParams,
    ModelFieldFontsParams, ModelFieldsOnTemplatesParams, CardTemplateData, CreateModelParams,
    ModelTemplatesParams, ModelStylingParams, UpdateModelTemplatesParams, UpdateModelStylingParams,
    UpdateModelTemplatesModelData, UpdateModelStylingModelData, FindAndReplaceInModelsParams,
    FindAndReplaceInModelsModelData, ModelTemplateRenameParams, ModelTemplateRepositionParams,
    ModelTemplateAddParams, ModelTemplateRemoveParams, ModelFieldRenameParams, ModelFieldRepositionParams,
    ModelFieldAddParams, ModelFieldRemoveParams, ModelFieldSetFontParams, ModelFieldSetFontSizeParams,
    ModelFieldSetDescriptionParams, # Model Actions
    GetCollectionStatsHTMLParams, CardReviewsParams, GetReviewsOfCardsParams, GetLatestReviewIDParams,
    InsertReviewsParams, ReviewTuple # Statistic Actions
)


logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="Anki MCP server",
    description="MCP server for Anki integration via Anki-Connect"
)

class NoParams(BaseModel):
    """Model for actions that require no parameters."""
    pass

_anki_client_instance: Optional[AsyncAnkiConnectClient] = None

async def get_anki_client() -> AsyncAnkiConnectClient:
    global _anki_client_instance
    if _anki_client_instance is None:
        _anki_client_instance = AsyncAnkiConnectClient()
        await _anki_client_instance._ensure_client()
    return _anki_client_instance

async def _execute_anki_request(action: str, params_model: BaseModel) -> Any:
    client = await get_anki_client()
    return await client.request(action=action, model=params_model)
        

# --- Annotations ---
# For tools that primarily read data and are not expected to have side effects.
READ_ONLY_ANNOTATIONS = ToolAnnotations(read_only_hint=True, open_world_hint=False, idempotent_hint=True)
# For tools that modify data but are idempotent (multiple identical calls have the same effect as one).
IDEMPOTENT_WRITE_ANNOTATIONS = ToolAnnotations(read_only_hint=False, open_world_hint=False, idempotent_hint=True)
# For tools that modify data and are NOT idempotent (multiple calls have cumulative effects or different outcomes).
NON_IDEMPOTENT_WRITE_ANNOTATIONS = ToolAnnotations(read_only_hint=False, open_world_hint=False, idempotent_hint=False)
# For tools that are destructive (e.g., delete data).
DESTRUCTIVE_ANNOTATIONS = ToolAnnotations(read_only_hint=False, open_world_hint=False, idempotent_hint=False, destructive_hint=True)
# For tools whose idempotency is complex or depends heavily on Anki's internal state for that specific action.
# Defaulting to non-idempotent write if unsure, to be safe.
DEFAULT_WRITE_ANNOTATIONS = NON_IDEMPOTENT_WRITE_ANNOTATIONS


# --- Card Action Tools ---
@mcp.tool(name="anki_get_ease_factors", description="Returns an array with the ease factor for each of the given cards.", annotations=READ_ONLY_ANNOTATIONS)
async def get_ease_factors_tool(params: GetEaseFactorsParams) -> List[int]:
    return await _execute_anki_request("getEaseFactors", params)

@mcp.tool(name="anki_set_ease_factors", description="Sets ease factor of cards by card ID.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def set_ease_factors_tool(params: SetEaseFactorsParams) -> List[bool]:
    return await _execute_anki_request("setEaseFactors", params)

@mcp.tool(name="anki_set_specific_value_of_card", description="Sets specific value of a single card. Some keys require 'warning_check'.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def set_specific_value_of_card_tool(params: SetSpecificValueOfCardParams) -> List[bool]:
    return await _execute_anki_request("setSpecificValueOfCard", params)

@mcp.tool(name="anki_suspend_cards", description="Suspend cards by card ID.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def suspend_cards_tool(params: SuspendCardsParams) -> bool:
    return await _execute_anki_request("suspend", params)

@mcp.tool(name="anki_unsuspend_cards", description="Unsuspend cards by card ID.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def unsuspend_cards_tool(params: UnsuspendCardsParams) -> bool:
    return await _execute_anki_request("unsuspend", params)

@mcp.tool(name="anki_is_card_suspended", description="Check if a card is suspended by its ID.", annotations=READ_ONLY_ANNOTATIONS)
async def is_card_suspended_tool(params: SuspendedCardParam) -> bool:
    return await _execute_anki_request("suspended", params)

@mcp.tool(name="anki_are_cards_suspended", description="Returns an array indicating whether each given card is suspended.", annotations=READ_ONLY_ANNOTATIONS)
async def are_cards_suspended_tool(params: AreSuspendedParams) -> List[Optional[bool]]:
    return await _execute_anki_request("areSuspended", params)

@mcp.tool(name="anki_are_cards_due", description="Returns an array indicating whether each given card is due.", annotations=READ_ONLY_ANNOTATIONS)
async def are_cards_due_tool(params: AreDueParams) -> List[bool]:
    return await _execute_anki_request("areDue", params)

@mcp.tool(name="anki_get_card_intervals", description="Returns intervals for given cards. Negative: seconds, Positive: days.", annotations=READ_ONLY_ANNOTATIONS)
async def get_card_intervals_tool(params: GetIntervalsParams) -> List[Union[int, List[int]]]:
    return await _execute_anki_request("getIntervals", params)

@mcp.tool(name="anki_find_cards", description="Returns an array of card IDs for a given Anki search query.", annotations=READ_ONLY_ANNOTATIONS)
async def find_cards_tool(params: FindCardsParams) -> List[int]:
    return await _execute_anki_request("findCards", params)

@mcp.tool(name="anki_convert_cards_to_notes", description="Returns an unordered array of note IDs for the given card IDs.", annotations=READ_ONLY_ANNOTATIONS)
async def convert_cards_to_notes_tool(params: CardsToNotesParams) -> List[int]:
    return await _execute_anki_request("cardsToNotes", params)

@mcp.tool(name="anki_get_cards_modification_time", description="Returns modification times for each card ID.", annotations=READ_ONLY_ANNOTATIONS)
async def get_cards_modification_time_tool(params: CardsModTimeParams) -> List[Dict[str, Any]]:
    return await _execute_anki_request("cardsModTime", params)

@mcp.tool(name="anki_get_cards_info", description="Returns detailed information for a list of card IDs.", annotations=READ_ONLY_ANNOTATIONS)
async def get_cards_info_tool(params: CardsInfoParams) -> List[Dict[str, Any]]:
    return await _execute_anki_request("cardsInfo", params)

@mcp.tool(name="anki_forget_cards", description="Forget cards, making them new again.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # Forgetting an already new card has same effect
async def forget_cards_tool(params: ForgetCardsParams) -> None:
    return await _execute_anki_request("forgetCards", params)

@mcp.tool(name="anki_relearn_cards", description="Mark cards for relearning.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # Relearning an already relearning card
async def relearn_cards_tool(params: RelearnCardsParams) -> None:
    return await _execute_anki_request("relearnCards", params)

@mcp.tool(name="anki_answer_cards", description="Answer cards. Ease is 1 (Again) to 4 (Easy).", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Answering changes state non-idempotently
async def answer_cards_tool(params: AnswerCardsParams) -> List[bool]:
    return await _execute_anki_request("answerCards", params)

@mcp.tool(name="anki_set_card_due_date", description="Set due date for cards. Turns new cards into review cards.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def set_card_due_date_tool(params: SetDueDateParams) -> bool:
    return await _execute_anki_request("setDueDate", params)

# --- Deck Action Tools ---
@mcp.tool(name="anki_get_deck_names", description="Gets the complete list of deck names.", annotations=READ_ONLY_ANNOTATIONS)
async def get_deck_names_tool(params: NoParams) -> List[str]:
    return await _execute_anki_request("deckNames", params)

@mcp.tool(name="anki_get_deck_names_and_ids", description="Gets deck names and their respective IDs.", annotations=READ_ONLY_ANNOTATIONS)
async def get_deck_names_and_ids_tool(params: NoParams) -> Dict[str, int]:
    return await _execute_anki_request("deckNamesAndIds", params)

@mcp.tool(name="anki_get_decks_containing_cards", description="Returns an object mapping deck names to lists of specified card IDs they contain.", annotations=READ_ONLY_ANNOTATIONS)
async def get_decks_containing_cards_tool(params: GetDecksParams) -> Dict[str, List[int]]:
    return await _execute_anki_request("getDecks", params)

@mcp.tool(name="anki_create_deck", description="Creates a new empty deck. Does not overwrite existing decks.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # Creating an existing deck name does nothing new
async def create_deck_tool(params: CreateDeckParams) -> int:
    return await _execute_anki_request("createDeck", params)

@mcp.tool(name="anki_change_deck_for_cards", description="Moves specified cards to a different deck, creating it if necessary.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def change_deck_for_cards_tool(params: ChangeDeckParams) -> None:
    return await _execute_anki_request("changeDeck", params)

@mcp.tool(name="anki_delete_decks", description="Deletes specified decks. 'cardsToo' must be true.", annotations=DESTRUCTIVE_ANNOTATIONS)
async def delete_decks_tool(params: DeleteDecksParams) -> None:
    return await _execute_anki_request("deleteDecks", params)

@mcp.tool(name="anki_get_deck_config", description="Gets the configuration group object for the given deck.", annotations=READ_ONLY_ANNOTATIONS)
async def get_deck_config_tool(params: GetDeckConfigParams) -> Dict[str, Any]:
    return await _execute_anki_request("getDeckConfig", params)

@mcp.tool(name="anki_save_deck_config", description="Saves the given deck configuration group.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def save_deck_config_tool(params: SaveDeckConfigParams) -> bool:
    return await _execute_anki_request("saveDeckConfig", params)

@mcp.tool(name="anki_set_deck_config_id_for_decks", description="Changes the configuration group for the given decks.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def set_deck_config_id_for_decks_tool(params: SetDeckConfigIdParams) -> bool:
    return await _execute_anki_request("setDeckConfigId", params)

@mcp.tool(name="anki_clone_deck_config", description="Creates a new deck configuration group by cloning an existing one.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Cloning again creates another new config
async def clone_deck_config_tool(params: CloneDeckConfigIdParams) -> Union[int, bool]:
    return await _execute_anki_request("cloneDeckConfigId", params)

@mcp.tool(name="anki_remove_deck_config", description="Removes the deck configuration group with the given ID.", annotations=DESTRUCTIVE_ANNOTATIONS)
async def remove_deck_config_tool(params: RemoveDeckConfigIdParams) -> bool:
    return await _execute_anki_request("removeDeckConfigId", params)

@mcp.tool(name="anki_get_deck_stats", description="Gets statistics (total cards, due cards, etc.) for the given decks.", annotations=READ_ONLY_ANNOTATIONS)
async def get_deck_stats_tool(params: GetDeckStatsParams) -> Dict[str, Any]:
    return await _execute_anki_request("getDeckStats", params)

# --- Note Action Tools ---
@mcp.tool(name="anki_add_note", description="Creates a new note. Options control duplicate handling.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # allowDuplicate=True makes it non-idempotent
async def add_note_tool(params: AddNoteParams) -> Optional[int]:
    return await _execute_anki_request("addNote", params)

@mcp.tool(name="anki_add_notes", description="Creates multiple notes.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS)
async def add_notes_tool(params: AddNotesParams) -> List[Optional[int]]:
    return await _execute_anki_request("addNotes", params)

@mcp.tool(name="anki_can_add_notes", description="Checks if a list of candidate notes can be added.", annotations=READ_ONLY_ANNOTATIONS)
async def can_add_notes_tool(params: CanAddNotesParams) -> List[bool]:
    return await _execute_anki_request("canAddNotes", params)

@mcp.tool(name="anki_can_add_notes_with_error_detail", description="Checks if notes can be added, returning detailed error messages.", annotations=READ_ONLY_ANNOTATIONS)
async def can_add_notes_with_error_detail_tool(params: CanAddNotesWithErrorDetailParams) -> List[Dict[str, Any]]:
    return await _execute_anki_request("canAddNotesWithErrorDetail", params)

@mcp.tool(name="anki_update_note_fields", description="Modifies the fields of an existing note. Can include media.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def update_note_fields_tool(params: UpdateNoteFieldsParams) -> None:
    return await _execute_anki_request("updateNoteFields", params)

@mcp.tool(name="anki_update_note", description="Modifies the fields and/or tags of an existing note. Can include media.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def update_note_tool(params: UpdateNoteParams) -> None:
    return await _execute_anki_request("updateNote", params)

@mcp.tool(name="anki_update_note_model", description="Updates the model, fields, and tags of an existing note.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def update_note_model_tool(params: UpdateNoteModelParams) -> None:
    return await _execute_anki_request("updateNoteModel", params)

@mcp.tool(name="anki_update_note_tags", description="Sets a note's tags by note ID, removing old tags.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def update_note_tags_tool(params: UpdateNoteTagsParams) -> None:
    return await _execute_anki_request("updateNoteTags", params)

@mcp.tool(name="anki_get_note_tags", description="Gets a note's tags by note ID.", annotations=READ_ONLY_ANNOTATIONS)
async def get_note_tags_tool(params: GetNoteTagsParams) -> List[str]:
    return await _execute_anki_request("getNoteTags", params)

@mcp.tool(name="anki_add_tags_to_notes", description="Adds specified tags to a list of notes.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # Adding existing tag is idempotent
async def add_tags_to_notes_tool(params: AddTagsParams) -> None:
    return await _execute_anki_request("addTags", params)

@mcp.tool(name="anki_remove_tags_from_notes", description="Removes specified tags from a list of notes.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # Removing non-existent tag is idempotent
async def remove_tags_from_notes_tool(params: RemoveTagsParams) -> None:
    return await _execute_anki_request("removeTags", params)

@mcp.tool(name="anki_get_all_tags", description="Gets the complete list of tags for the current user.", annotations=READ_ONLY_ANNOTATIONS)
async def get_all_tags_tool(params: NoParams) -> List[str]:
    return await _execute_anki_request("getTags", params)

@mcp.tool(name="anki_clear_unused_tags", description="Clears all unused tags in the collection.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # Effect is same if called multiple times on same set of unused tags
async def clear_unused_tags_tool(params: NoParams) -> None:
    return await _execute_anki_request("clearUnusedTags", params)

@mcp.tool(name="anki_replace_tags_in_notes", description="Replaces a specific tag with another tag for a list of notes.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def replace_tags_in_notes_tool(params: ReplaceTagsParams) -> None:
    return await _execute_anki_request("replaceTags", params)

@mcp.tool(name="anki_replace_tags_in_all_notes", description="Replaces a tag with another tag across all notes in the collection.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def replace_tags_in_all_notes_tool(params: ReplaceTagsInAllNotesParams) -> None:
    return await _execute_anki_request("replaceTagsInAllNotes", params)

@mcp.tool(name="anki_find_notes", description="Returns an array of note IDs for a given Anki search query.", annotations=READ_ONLY_ANNOTATIONS)
async def find_notes_tool(params: FindNotesParams) -> List[int]:
    return await _execute_anki_request("findNotes", params)

@mcp.tool(name="anki_get_notes_info", description="Returns detailed information for specified note IDs or notes matching a query.", annotations=READ_ONLY_ANNOTATIONS)
async def get_notes_info_tool(params: NotesInfoParams) -> List[Dict[str, Any]]:
    return await _execute_anki_request("notesInfo", params)

@mcp.tool(name="anki_get_notes_modification_time", description="Returns modification times for each note ID.", annotations=READ_ONLY_ANNOTATIONS)
async def get_notes_modification_time_tool(params: NotesModTimeParamsNotes) -> List[Dict[str, Any]]:
    return await _execute_anki_request("notesModTime", params)

@mcp.tool(name="anki_delete_notes", description="Deletes notes with the given IDs, including all their cards.", annotations=DESTRUCTIVE_ANNOTATIONS)
async def delete_notes_tool(params: DeleteNotesParams) -> None: # Corrected from NotesParam to DeleteNotesParams
    return await _execute_anki_request("deleteNotes", params)

@mcp.tool(name="anki_remove_empty_notes", description="Removes all empty notes for the current user.", annotations=DESTRUCTIVE_ANNOTATIONS) # Potentially destructive if notes were intended to be filled later
async def remove_empty_notes_tool(params: NoParams) -> None:
    return await _execute_anki_request("removeEmptyNotes", params)

# --- Graphical Action Tools ---
@mcp.tool(name="anki_gui_browse", description="Invokes the Card Browser dialog and searches for a given query.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Interacts with GUI, can change selection
async def gui_browse_tool(params: GuiBrowseParams) -> List[int]:
    return await _execute_anki_request("guiBrowse", params)

@mcp.tool(name="anki_gui_select_card", description="Finds the open Card Browser and selects a card.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Changes GUI selection
async def gui_select_card_tool(params: GuiSelectCardParams) -> bool:
    return await _execute_anki_request("guiSelectCard", params)

@mcp.tool(name="anki_gui_selected_notes", description="Returns an array of selected note IDs from the Card Browser.", annotations=READ_ONLY_ANNOTATIONS)
async def gui_selected_notes_tool(params: NoParams) -> List[int]:
    return await _execute_anki_request("guiSelectedNotes", params)

@mcp.tool(name="anki_gui_add_cards", description="Invokes the Add Cards dialog, presetting fields.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Opens a new GUI window
async def gui_add_cards_tool(params: GuiAddCardsParams) -> Optional[int]: # Returns potential note ID
    return await _execute_anki_request("guiAddCards", params)

@mcp.tool(name="anki_gui_edit_note", description="Opens the Edit dialog for a given note ID.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Opens a new GUI window
async def gui_edit_note_tool(params: GuiEditNoteParams) -> None:
    return await _execute_anki_request("guiEditNote", params)

@mcp.tool(name="anki_gui_current_card", description="Returns information about the current card if in review mode.", annotations=READ_ONLY_ANNOTATIONS)
async def gui_current_card_tool(params: NoParams) -> Optional[Dict[str, Any]]:
    return await _execute_anki_request("guiCurrentCard", params)

@mcp.tool(name="anki_gui_start_card_timer", description="Starts or resets the timer for the current card.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Modifies timer state
async def gui_start_card_timer_tool(params: NoParams) -> bool:
    return await _execute_anki_request("guiStartCardTimer", params)

@mcp.tool(name="anki_gui_show_question", description="Shows question text for the current card.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Changes GUI state
async def gui_show_question_tool(params: NoParams) -> bool:
    return await _execute_anki_request("guiShowQuestion", params)

@mcp.tool(name="anki_gui_show_answer", description="Shows answer text for the current card.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Changes GUI state
async def gui_show_answer_tool(params: NoParams) -> bool:
    return await _execute_anki_request("guiShowAnswer", params)

@mcp.tool(name="anki_gui_answer_card", description="Answers the current card.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Modifies card state and GUI
async def gui_answer_card_tool(params: GuiAnswerCardParams) -> bool:
    return await _execute_anki_request("guiAnswerCard", params)

@mcp.tool(name="anki_gui_undo", description="Undo the last action/card.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Reverts state
async def gui_undo_tool(params: NoParams) -> bool:
    return await _execute_anki_request("guiUndo", params)

@mcp.tool(name="anki_gui_deck_overview", description="Opens the Deck Overview dialog for the named deck.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Changes GUI view
async def gui_deck_overview_tool(params: GuiDeckOverviewParams) -> bool:
    return await _execute_anki_request("guiDeckOverview", params)

@mcp.tool(name="anki_gui_deck_browser", description="Opens the Deck Browser dialog.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Changes GUI view
async def gui_deck_browser_tool(params: NoParams) -> None:
    return await _execute_anki_request("guiDeckBrowser", params)

@mcp.tool(name="anki_gui_deck_review", description="Starts review for the named deck.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Changes GUI view and starts review state
async def gui_deck_review_tool(params: GuiDeckReviewParams) -> bool:
    return await _execute_anki_request("guiDeckReview", params)

@mcp.tool(name="anki_gui_import_file", description="Invokes the Import dialog with an optional file path.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Opens GUI dialog
async def gui_import_file_tool(params: GuiImportFileParams) -> None:
    return await _execute_anki_request("guiImportFile", params)

@mcp.tool(name="anki_gui_exit_anki", description="Schedules a request to gracefully close Anki.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Destructive to application session
async def gui_exit_anki_tool(params: NoParams) -> None:
    return await _execute_anki_request("guiExitAnki", params)

@mcp.tool(name="anki_gui_check_database", description="Requests a database check.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Can modify database if issues found
async def gui_check_database_tool(params: NoParams) -> bool:
    return await _execute_anki_request("guiCheckDatabase", params)

# --- Media Action Tools ---
@mcp.tool(name="anki_store_media_file", description="Stores a file in the media folder.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # If deleteExisting=True (default), it's idempotent. If False, non-idempotent.
async def store_media_file_tool(params: StoreMediaFileParams) -> str: # Returns filename
    return await _execute_anki_request("storeMediaFile", params)

@mcp.tool(name="anki_retrieve_media_file", description="Retrieves the base64-encoded contents of a media file.", annotations=READ_ONLY_ANNOTATIONS)
async def retrieve_media_file_tool(params: RetrieveMediaFileParams) -> Union[str, bool]: # Returns base64 string or false
    return await _execute_anki_request("retrieveMediaFile", params)

@mcp.tool(name="anki_get_media_files_names", description="Gets the names of media files matching a pattern.", annotations=READ_ONLY_ANNOTATIONS)
async def get_media_files_names_tool(params: GetMediaFilesNamesParams) -> List[str]:
    return await _execute_anki_request("getMediaFilesNames", params)

@mcp.tool(name="anki_get_media_dir_path", description="Gets the full path to the collection.media folder.", annotations=READ_ONLY_ANNOTATIONS)
async def get_media_dir_path_tool(params: NoParams) -> str:
    return await _execute_anki_request("getMediaDirPath", params)

@mcp.tool(name="anki_delete_media_file", description="Deletes a specified file from the media folder.", annotations=DESTRUCTIVE_ANNOTATIONS)
async def delete_media_file_tool(params: DeleteMediaFileParams) -> None:
    return await _execute_anki_request("deleteMediaFile", params)

# --- Miscellaneous Action Tools ---
@mcp.tool(name="anki_request_permission", description="Requests permission to use the API. Does not require API key.", annotations=READ_ONLY_ANNOTATIONS) # Does not change server state, but interacts with user
async def request_permission_tool(params: NoParams) -> Dict[str, Any]:
    return await _execute_anki_request("requestPermission", params)

@mcp.tool(name="anki_get_version", description="Gets the version of the Anki-Connect API.", annotations=READ_ONLY_ANNOTATIONS)
async def get_version_tool(params: NoParams) -> int:
    return await _execute_anki_request("version", params)

@mcp.tool(name="anki_api_reflect", description="Gets information about available Anki-Connect APIs.", annotations=READ_ONLY_ANNOTATIONS)
async def api_reflect_tool(params: ApiReflectParams) -> Dict[str, Any]:
    return await _execute_anki_request("apiReflect", params)

@mcp.tool(name="anki_sync_collection", description="Synchronizes the local Anki collections with AnkiWeb.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Sync state changes
async def sync_collection_tool(params: NoParams) -> None: # Anki-Connect action is 'sync'
    return await _execute_anki_request("sync", params)

@mcp.tool(name="anki_get_profiles", description="Retrieve the list of profiles.", annotations=READ_ONLY_ANNOTATIONS)
async def get_profiles_tool(params: NoParams) -> List[str]:
    return await _execute_anki_request("getProfiles", params)

@mcp.tool(name="anki_get_active_profile", description="Retrieve the active profile.", annotations=READ_ONLY_ANNOTATIONS)
async def get_active_profile_tool(params: NoParams) -> str:
    return await _execute_anki_request("getActiveProfile", params)

@mcp.tool(name="anki_load_profile", description="Selects the specified profile.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS) # Loading same profile is idempotent
async def load_profile_tool(params: LoadProfileParams) -> bool:
    return await _execute_anki_request("loadProfile", params)

@mcp.tool(name="anki_multi_action", description="Performs multiple actions in one request.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Depends on sub-actions
async def multi_action_tool(params: MultiParams) -> List[Any]: # Anki-Connect action is 'multi'
    return await _execute_anki_request("multi", params)

@mcp.tool(name="anki_export_package", description="Exports a given deck in .apkg format.", annotations=READ_ONLY_ANNOTATIONS) # Creates a file, but doesn't change Anki collection state itself.
async def export_package_tool(params: ExportPackageParams) -> bool:
    return await _execute_anki_request("exportPackage", params)

@mcp.tool(name="anki_import_package", description="Imports a file in .apkg format into the collection.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Modifies collection
async def import_package_tool(params: ImportPackageParams) -> bool:
    return await _execute_anki_request("importPackage", params)

@mcp.tool(name="anki_reload_collection", description="Tells Anki to reload all data from the database.", annotations=DEFAULT_WRITE_ANNOTATIONS) # Can have side effects if data changed externally
async def reload_collection_tool(params: NoParams) -> None:
    return await _execute_anki_request("reloadCollection", params)

# --- Model Action Tools ---
@mcp.tool(name="anki_get_model_names", description="Gets the complete list of model names.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_names_tool(params: NoParams) -> List[str]:
    return await _execute_anki_request("modelNames", params)

@mcp.tool(name="anki_get_model_names_and_ids", description="Gets model names and their corresponding IDs.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_names_and_ids_tool(params: NoParams) -> Dict[str, int]:
    return await _execute_anki_request("modelNamesAndIds", params)

@mcp.tool(name="anki_find_models_by_id", description="Gets a list of models for the provided model IDs.", annotations=READ_ONLY_ANNOTATIONS)
async def find_models_by_id_tool(params: FindModelsByIdParams) -> List[Dict[str, Any]]:
    return await _execute_anki_request("findModelsById", params)

@mcp.tool(name="anki_find_models_by_name", description="Gets a list of models for the provided model names.", annotations=READ_ONLY_ANNOTATIONS)
async def find_models_by_name_tool(params: FindModelsByNameParams) -> List[Dict[str, Any]]:
    return await _execute_anki_request("findModelsByName", params)

@mcp.tool(name="anki_get_model_field_names", description="Gets the list of field names for a model.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_field_names_tool(params: ModelFieldNamesParams) -> List[str]:
    return await _execute_anki_request("modelFieldNames", params)

@mcp.tool(name="anki_get_model_field_descriptions", description="Gets field descriptions for a model.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_field_descriptions_tool(params: ModelFieldDescriptionsParams) -> List[str]:
    return await _execute_anki_request("modelFieldDescriptions", params)

@mcp.tool(name="anki_get_model_field_fonts", description="Gets fonts and sizes for fields in a model.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_field_fonts_tool(params: ModelFieldFontsParams) -> Dict[str, Dict[str, Any]]:
    return await _execute_anki_request("modelFieldFonts", params)

@mcp.tool(name="anki_get_model_fields_on_templates", description="Indicates fields on question/answer sides of templates for a model.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_fields_on_templates_tool(params: ModelFieldsOnTemplatesParams) -> Dict[str, List[List[str]]]:
    return await _execute_anki_request("modelFieldsOnTemplates", params)

@mcp.tool(name="anki_create_model", description="Creates a new model.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Creating same model name might error or create variants
async def create_model_tool(params: CreateModelParams) -> Dict[str, Any]: # Returns model object
    return await _execute_anki_request("createModel", params)

@mcp.tool(name="anki_get_model_templates", description="Gets template content for each card in a model.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_templates_tool(params: ModelTemplatesParams) -> Dict[str, Dict[str, str]]:
    return await _execute_anki_request("modelTemplates", params)

@mcp.tool(name="anki_get_model_styling", description="Gets the CSS styling for a model.", annotations=READ_ONLY_ANNOTATIONS)
async def get_model_styling_tool(params: ModelStylingParams) -> Dict[str, str]:
    return await _execute_anki_request("modelStyling", params)

@mcp.tool(name="anki_update_model_templates", description="Modify the templates of an existing model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def update_model_templates_tool(params: UpdateModelTemplatesParams) -> None:
    return await _execute_anki_request("updateModelTemplates", params)

@mcp.tool(name="anki_update_model_styling", description="Modify the CSS styling of an existing model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def update_model_styling_tool(params: UpdateModelStylingParams) -> None:
    return await _execute_anki_request("updateModelStyling", params)

@mcp.tool(name="anki_find_and_replace_in_models", description="Find and replace string in model templates/CSS.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def find_and_replace_in_models_tool(params: FindAndReplaceInModelsParams) -> int: # Returns number of changes
    return await _execute_anki_request("findAndReplaceInModels", params)

@mcp.tool(name="anki_rename_model_template", description="Renames a template in an existing model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def rename_model_template_tool(params: ModelTemplateRenameParams) -> None:
    return await _execute_anki_request("modelTemplateRename", params)

@mcp.tool(name="anki_reposition_model_template", description="Repositions a template in an existing model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def reposition_model_template_tool(params: ModelTemplateRepositionParams) -> None:
    return await _execute_anki_request("modelTemplateReposition", params)

@mcp.tool(name="anki_add_model_template", description="Adds a template to an existing model.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Adding same template name might error or create variants
async def add_model_template_tool(params: ModelTemplateAddParams) -> None:
    return await _execute_anki_request("modelTemplateAdd", params)

@mcp.tool(name="anki_remove_model_template", description="Removes a template from an existing model.", annotations=DESTRUCTIVE_ANNOTATIONS)
async def remove_model_template_tool(params: ModelTemplateRemoveParams) -> None:
    return await _execute_anki_request("modelTemplateRemove", params)

@mcp.tool(name="anki_rename_model_field", description="Rename a field in a given model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def rename_model_field_tool(params: ModelFieldRenameParams) -> None:
    return await _execute_anki_request("modelFieldRename", params)

@mcp.tool(name="anki_reposition_model_field", description="Reposition a field within a model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def reposition_model_field_tool(params: ModelFieldRepositionParams) -> None:
    return await _execute_anki_request("modelFieldReposition", params)

@mcp.tool(name="anki_add_model_field", description="Creates a new field within a given model.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Adding same field name might error
async def add_model_field_tool(params: ModelFieldAddParams) -> None:
    return await _execute_anki_request("modelFieldAdd", params)

@mcp.tool(name="anki_remove_model_field", description="Deletes a field within a given model.", annotations=DESTRUCTIVE_ANNOTATIONS)
async def remove_model_field_tool(params: ModelFieldRemoveParams) -> None:
    return await _execute_anki_request("modelFieldRemove", params)

@mcp.tool(name="anki_set_model_field_font", description="Sets the font for a field within a model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def set_model_field_font_tool(params: ModelFieldSetFontParams) -> None:
    return await _execute_anki_request("modelFieldSetFont", params)

@mcp.tool(name="anki_set_model_field_font_size", description="Sets the font size for a field within a model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def set_model_field_font_size_tool(params: ModelFieldSetFontSizeParams) -> None:
    return await _execute_anki_request("modelFieldSetFontSize", params)

@mcp.tool(name="anki_set_model_field_description", description="Sets the description for a field within a model.", annotations=IDEMPOTENT_WRITE_ANNOTATIONS)
async def set_model_field_description_tool(params: ModelFieldSetDescriptionParams) -> bool:
    return await _execute_anki_request("modelFieldSetDescription", params)

# --- Statistic Action Tools ---
@mcp.tool(name="anki_get_num_cards_reviewed_today", description="Gets the count of cards reviewed today.", annotations=READ_ONLY_ANNOTATIONS)
async def get_num_cards_reviewed_today_tool(params: NoParams) -> int:
    return await _execute_anki_request("getNumCardsReviewedToday", params)

@mcp.tool(name="anki_get_num_cards_reviewed_by_day", description="Gets the number of cards reviewed, grouped by day.", annotations=READ_ONLY_ANNOTATIONS)
async def get_num_cards_reviewed_by_day_tool(params: NoParams) -> List[Tuple[str, int]]:
    return await _execute_anki_request("getNumCardsReviewedByDay", params)

@mcp.tool(name="anki_get_collection_stats_html", description="Gets the collection statistics report as HTML.", annotations=READ_ONLY_ANNOTATIONS)
async def get_collection_stats_html_tool(params: GetCollectionStatsHTMLParams) -> str:
    return await _execute_anki_request("getCollectionStatsHTML", params)

@mcp.tool(name="anki_get_card_reviews", description="Requests all card reviews for a specified deck after a certain time.", annotations=READ_ONLY_ANNOTATIONS)
async def get_card_reviews_tool(params: CardReviewsParams) -> List[ReviewTuple]:
    return await _execute_anki_request("cardReviews", params)

@mcp.tool(name="anki_get_reviews_of_cards", description="Requests all card reviews for each specified card ID.", annotations=READ_ONLY_ANNOTATIONS)
async def get_reviews_of_cards_tool(params: GetReviewsOfCardsParams) -> Dict[str, List[Dict[str, Any]]]:
    return await _execute_anki_request("getReviewsOfCards", params)

@mcp.tool(name="anki_get_latest_review_id", description="Returns the Unix time of the latest review for a deck.", annotations=READ_ONLY_ANNOTATIONS)
async def get_latest_review_id_tool(params: GetLatestReviewIDParams) -> int:
    return await _execute_anki_request("getLatestReviewID", params)

@mcp.tool(name="anki_insert_reviews", description="Inserts given reviews into the database.", annotations=NON_IDEMPOTENT_WRITE_ANNOTATIONS) # Inserting reviews changes state
async def insert_reviews_tool(params: InsertReviewsParams) -> None:
    return await _execute_anki_request("insertReviews", params)

@mcp.prompt()
def prompt_add_note_guidance() -> str:
    """Provides guidance on how to add a new note to Anki."""
    return (
        "To add a new note to Anki, you need to provide the following information:\n"
        "If you are unsure about the following parameters, use mcp server to ask about the parameters.\n"
        "1.  **Deck Name**: The name of the deck where the note will be added (e.g., 'Default', 'Chinese::Vocabulary').\n"
        "2.  **Model Name**: The name of the note type (template) to use (e.g., 'Basic', 'Cloze', 'Basic (and reversed card)').\n"
        "3.  **Fields**: A dictionary where keys are the field names of the chosen model and values are the content for those fields.\n"
        "    - Card content can use HTML for formatting.\n"
        "    - For standard fields, `{{field_name}}` in a card template will be replaced by the field's content.\n"
        "    - If you are using a 'Cloze' model, use `{{c1::text_to_cloze}}` to create a cloze deletion for 'text_to_cloze'. You can use c2, c3, etc., for multiple clozes on the same note.\n"
        "4.  **Tags (Optional)**: A list of strings to tag the note with (e.g., ['vocab', 'priority1']).\n"
        "5.  **Media (Optional)**: You can also include audio, video, or picture files to be embedded in the note's fields."
    )

@mcp.prompt()
def prompt_search_filter_guidance() -> str:
    """Provides a summary of Anki search syntax for filtering cards and notes."""
    return (
        "Anki's search syntax allows for powerful filtering. Here's a quick guide:\n"
        "- **Simple terms**: `word` (matches 'word', 'wording'), `word1 word2` (matches notes with both), `word1 or word2`.\n"
        "- **Exact phrase**: `\"exact phrase\"`.\n"
        "- **Wildcards**: `d_g` (dog, dig), `d*g` (dg, dog, doing).\n"
        "- **Word boundary**: `w:dog` (matches 'dog', not 'doggy'). `w:dog*` (dog, doggy).\n"
        "- **Negation**: `-cat` (without 'cat').\n"
        "- **Field specific**: `front:text` (Front field is exactly 'text'), `front:*text*` (Front field contains 'text').\n"
        "- **Tags**: `tag:animal`, `tag:none`, `tag:ani*`.\n"
        "- **Deck**: `deck:French`, `deck:\"French Words\"`, `deck:filtered`.\n"
        "- **Card type/template**: `card:Forward`, `card:1` (first template).\n"
        "- **Note type**: `note:Basic`.\n"
        "- **Regular Expressions**: `re:^start.*end$` (prefix search with `re:`).\n"
        "- **Card State**: `is:due`, `is:new`, `is:learn`, `is:review`, `is:suspended`, `is:buried`.\n"
        "- **Flags**: `flag:1` (red), `flag:2` (orange), etc.\n"
        "- **Properties**: `prop:ivl>=10` (interval >= 10 days), `prop:due=1` (due tomorrow), `prop:reps<10`.\n"
        "- **Recent Events**: `added:7` (added in last 7 days), `rated:1` (answered today), `rated:7:1` (answered 'Again' in last 7 days), `introduced:1` (first answered today).\n"
        "- **Object IDs**: `nid:12345` (note ID), `cid:12345` (card ID).\n"
        "Combine terms for more specific searches, e.g., `deck:Default tag:important is:due`."
    )

@mcp.prompt()
def prompt_media_upload_guidance() -> str:
    """Provides guidance on how to upload media files to Anki."""
    return (
        "When working with media files (audio, video, images) in Anki via Anki-Connect:\n"
        "1.  **Base64 Encoding**: If you are providing the file content directly (not via a URL or local path), the content must be Base64 encoded.\n"
        "2.  **Standalone Media Upload**: You can use a specific API tool (like 'anki.store_media_file') to upload a media file directly to Anki's media collection. You'll need to provide the desired filename and the content (either as Base64 data, a local server path, or a URL).\n"
        "3.  **Media with Note Creation/Update**: When adding or updating a note (e.g., using 'anki.add_note' or 'anki.update_note_fields'), you can include 'audio', 'video', or 'picture' arrays in the note parameters. Each item in these arrays should specify:\n"
        "    - `filename`: The name the file should have in Anki.\n"
        "    - `data`, `path`, or `url`: The source of the media file.\n"
        "    - `fields`: A list of field names where this media should be embedded (e.g., `['Front', 'Sound']`).\n"
        "    - `skipHash` (optional): An MD5 hash to prevent re-downloading/storing identical files."
    )


# --- Main execution ---
def run_server() -> None:
    """Start the MCP server"""
    logging.basicConfig(level=config.mcp_server.log_level)
    logger.info(f"Starting Anki-MCP-Server")
    mcp.run()