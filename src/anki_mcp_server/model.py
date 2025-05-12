from typing import List, Dict, Any, Optional, Tuple, Union, Literal
from pydantic import BaseModel, Field

# Common Base Models
class CardsParam(BaseModel):
    cards: List[int] = Field(..., description="A list of card IDs (integers).")

class CardParam(BaseModel):
    card: int = Field(..., description="A single card ID (integer).")

class NotesParam(BaseModel):
    notes: List[int] = Field(..., description="A list of note IDs (integers).")

class NoteIdParam(BaseModel):
    note: int = Field(..., description="A single note ID (integer).")

class DeckNameParam(BaseModel):
    deck: str = Field(..., description="The name of the deck.")

class DeckNamesParam(BaseModel):
    decks: List[str] = Field(..., description="A list of deck names.")

class QueryParam(BaseModel):
    query: str = Field(..., description="An Anki search query string (e.g., 'deck:current', 'tag:important'). Refer to Anki search syntax for more details.")

class ModelNameParam(BaseModel):
    modelName: str = Field(..., description="The name of the Anki model (note type).")

# --- Deck Action Params ---
class GetDecksParams(CardsParam):
    pass

class CreateDeckParams(DeckNameParam):
    pass

class ChangeDeckParams(CardsParam):
    deck: str = Field(..., description="The target deck name. The deck will be created if it doesn't exist.")

class DeleteDecksParams(BaseModel):
    decks: List[str] = Field(..., description="A list of deck names to delete.")
    cardsToo: Literal[True] = Field(..., description="Must be true to confirm deletion of cards within the decks.")

class GetDeckConfigParams(DeckNameParam):
    pass

class DeckConfigNewOptions(BaseModel):
    bury: Optional[bool] = Field(None, description="Whether to bury new siblings.")
    order: Optional[int] = Field(None, description="Order of new cards (0 for due, 1 for random).")
    initialFactor: Optional[int] = Field(None, description="Initial ease factor for new cards.")
    perDay: Optional[int] = Field(None, description="Maximum number of new cards to introduce per day.")
    delays: Optional[List[float]] = Field(None, description="Learning steps for new cards (in minutes).")
    separate: Optional[bool] = Field(None, description="Whether to separate new cards and reviews.")
    ints: Optional[List[int]] = Field(None, description="Intervals for new cards after graduating (in days).")

class DeckConfigLapseOptions(BaseModel):
    leechFails: Optional[int] = Field(None, description="Number of lapses before a card is marked as a leech.")
    delays: Optional[List[float]] = Field(None, description="Relearning steps for lapsed cards (in minutes).")
    minInt: Optional[int] = Field(None, description="Minimum interval for a lapsed card (in days).")
    leechAction: Optional[int] = Field(None, description="Action to take on a leech (0 for suspend, 1 for tag only).")
    mult: Optional[float] = Field(None, description="Interval multiplier for lapsed cards (e.g., 0 for reset).")

class DeckConfigRevOptions(BaseModel):
    bury: Optional[bool] = Field(None, description="Whether to bury review siblings.")
    ivlFct: Optional[float] = Field(None, description="Interval factor.")
    ease4: Optional[float] = Field(None, description="Bonus for answering 'Easy'.")
    maxIvl: Optional[int] = Field(None, description="Maximum review interval (in days).")
    perDay: Optional[int] = Field(None, description="Maximum number of reviews per day.")
    minSpace: Optional[int] = Field(None, description="Minimum space between sibling reviews (for v1 scheduler, deprecated).")
    fuzz: Optional[float] = Field(None, description="Fuzz factor for review intervals.")

class DeckConfigObject(BaseModel):
    id: int = Field(..., description="The ID of the deck configuration group.")
    name: str = Field(..., description="The name of the deck configuration group.")
    mod: Optional[int] = Field(None, description="Modification timestamp.")
    usn: Optional[int] = Field(None, description="Update sequence number.")
    dyn: Optional[bool] = Field(None, description="Whether this is a dynamic (filtered) deck configuration.")
    autoplay: Optional[bool] = Field(None, description="Whether to autoplay audio.")
    timer: Optional[int] = Field(None, description="Timer setting (0 for no timer, 1 for timer enabled).")
    replayq: Optional[bool] = Field(None, description="Whether to replay audio/video on question side.")
    maxTaken: Optional[int] = Field(None, description="Maximum time in seconds to record for answering a card.")
    new: Optional[DeckConfigNewOptions] = None
    lapse: Optional[DeckConfigLapseOptions] = None
    rev: Optional[DeckConfigRevOptions] = None
    other: Optional[Dict[str, Any]] = Field(None, description="Catch-all for other less common or new config options.")

    class Config:
        extra = 'allow'

class SaveDeckConfigParams(BaseModel):
    config: DeckConfigObject = Field(..., description="The deck configuration object to save.")

class SetDeckConfigIdParams(DeckNamesParam):
    configId: int = Field(..., description="The ID of the deck configuration group to apply.")

class CloneDeckConfigIdParams(BaseModel):
    name: str = Field(..., description="The name for the new cloned deck configuration group.")
    cloneFrom: Optional[int] = Field(None, description="The ID of the deck configuration group to clone from. If None, clones from the default group.")

class RemoveDeckConfigIdParams(BaseModel):
    configId: int = Field(..., description="The ID of the deck configuration group to remove.")

class GetDeckStatsParams(DeckNamesParam):
    pass

# --- Card Action Params ---
class GetEaseFactorsParams(CardsParam):
    pass

class SetEaseFactorsParams(CardsParam):
    easeFactors: List[int] = Field(..., description="A list of ease factors (integers, e.g., 2500 for 250%%) corresponding to the cards.")

class SetSpecificValueOfCardParams(CardParam):
    keys: List[str] = Field(..., description="A list of card property keys to modify (e.g., 'flags', 'odue').")
    newValues: List[str] = Field(..., description="A list of new values corresponding to the keys. Values should be strings.")
    warning_check: Optional[bool] = Field(None, description="Set to true if modifying potentially risky card values.")

class SuspendCardsParams(CardsParam):
    pass

class UnsuspendCardsParams(CardsParam):
    pass

class SuspendedCardParam(CardParam):
    pass

class AreSuspendedParams(CardsParam):
    pass

class AreDueParams(CardsParam):
    pass

class GetIntervalsParams(CardsParam):
    complete: Optional[bool] = Field(False, description="If true, returns all intervals for each card; otherwise, only the most recent.")

class FindCardsParams(QueryParam):
    pass

class CardsToNotesParams(CardsParam):
    pass

class CardsModTimeParams(CardsParam):
    pass

class CardsInfoParams(CardsParam):
    pass

class ForgetCardsParams(CardsParam):
    pass

class RelearnCardsParams(CardsParam):
    pass

class CardAnswer(BaseModel):
    cardId: int = Field(..., description="The ID of the card being answered.")
    ease: int = Field(..., description="The ease rating (1 for Again, 2 for Hard, 3 for Good, 4 for Easy).")

class AnswerCardsParams(BaseModel):
    answers: List[CardAnswer] = Field(..., description="A list of card answers.")

class SetDueDateParams(CardsParam):
    days: str = Field(..., description="Due date specification string (e.g., '0', '1!', '3-7').")

# --- Note Action Params ---
class NoteMediaAsset(BaseModel):
    filename: str = Field(..., description="Desired filename for the media file.")
    data: Optional[str] = Field(None, description="Base64 encoded media content.")
    path: Optional[str] = Field(None, description="Absolute path to the media file.")
    url: Optional[str] = Field(None, description="URL to download the media file from.")
    skipHash: Optional[str] = Field(None, description="MD5 hash to skip download if matched.")
    fields: List[str] = Field(..., description="List of field names to embed media into.")

class DuplicateScopeOptionsStructure(BaseModel):
    deckName: Optional[str] = Field(None, description="Deck to use for duplicate checking. Null for target note's deck.")
    checkChildren: Optional[bool] = Field(False, description="Check for duplicates in child decks.")
    checkAllModels: Optional[bool] = Field(False, description="Check duplicates across all note types.")

class NoteOptionsStructure(BaseModel):
    allowDuplicate: Optional[bool] = Field(False, description="Allow adding duplicate notes.")
    duplicateScope: Optional[Literal["deck", "collection"]] = Field(None, description="Scope for duplicate checking.")
    duplicateScopeOptions: Optional[DuplicateScopeOptionsStructure] = Field(None, description="Options for duplicate scoping.")

class NoteToAdd(BaseModel):
    deckName: str = Field(..., description="Deck name for the new note.")
    modelName: str = Field(..., description="Model name for the new note.")
    fields: Dict[str, str] = Field(..., description="Dictionary of field names to content.")
    options: Optional[NoteOptionsStructure] = Field(None, description="Options for adding the note.")
    tags: Optional[List[str]] = Field(None, description="List of tags for the note.")
    audio: Optional[List[NoteMediaAsset]] = Field(None, description="Audio files to attach.")
    video: Optional[List[NoteMediaAsset]] = Field(None, description="Video files to attach.")
    picture: Optional[List[NoteMediaAsset]] = Field(None, description="Picture files to attach.")

class AddNoteParams(BaseModel):
    note: NoteToAdd = Field(..., description="The note object to be added.")

class AddNotesParams(BaseModel):
    notes: List[NoteToAdd] = Field(..., description="A list of note objects to be added.")

class NoteToCanAdd(BaseModel):
    deckName: str = Field(..., description="Name of the deck.")
    modelName: str = Field(..., description="Name of the model.")
    fields: Dict[str, str] = Field(..., description="Dictionary of field names to content.")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags.")
    options: Optional[NoteOptionsStructure] = Field(None, description="Optional settings for duplicate handling.")

class CanAddNotesParams(BaseModel):
    notes: List[NoteToCanAdd] = Field(..., description="List of note parameters to check.")

class CanAddNotesWithErrorDetailParams(CanAddNotesParams):
    pass

class NoteFieldsToUpdate(BaseModel):
    id: int = Field(..., description="ID of the note to update.")
    fields: Dict[str, str] = Field(..., description="Dictionary of field names to new content.")
    audio: Optional[List[NoteMediaAsset]] = Field(None, description="Audio files to add/update.")
    video: Optional[List[NoteMediaAsset]] = Field(None, description="Video files to add/update.")
    picture: Optional[List[NoteMediaAsset]] = Field(None, description="Picture files to add/update.")

class UpdateNoteFieldsParams(BaseModel):
    note: NoteFieldsToUpdate = Field(..., description="Note fields to update.")

class NoteToUpdate(BaseModel):
    id: int = Field(..., description="ID of the note to update.")
    fields: Optional[Dict[str, str]] = Field(None, description="Optional new field content.")
    tags: Optional[List[str]] = Field(None, description="Optional new list of tags (replaces existing).")
    audio: Optional[List[NoteMediaAsset]] = Field(None, description="Audio files to add/update. Requires 'fields'.")
    video: Optional[List[NoteMediaAsset]] = Field(None, description="Video files to add/update. Requires 'fields'.")
    picture: Optional[List[NoteMediaAsset]] = Field(None, description="Picture files to add/update. Requires 'fields'.")

class UpdateNoteParams(BaseModel):
    note: NoteToUpdate = Field(..., description="Note data to update.")

class NoteModelToUpdate(BaseModel):
    id: int = Field(..., description="ID of the note to update.")
    modelName: str = Field(..., description="New model name for the note.")
    fields: Dict[str, str] = Field(..., description="Dictionary of field names (of new model) to content.")
    tags: Optional[List[str]] = Field(None, description="Optional new list of tags.")

class UpdateNoteModelParams(BaseModel):
    note: NoteModelToUpdate = Field(..., description="Note data for updating model, fields, and tags.")

class UpdateNoteTagsParams(NoteIdParam):
    tags: List[str] = Field(..., description="List of tags to set (replaces existing).")

class GetNoteTagsParams(NoteIdParam):
    pass

class AddTagsParams(NotesParam):
    tags: Union[str, List[str]] = Field(..., description="A tag or list of tags to add.")

class RemoveTagsParams(NotesParam):
    tags: Union[str, List[str]] = Field(..., description="A tag or list of tags to remove.")

class ReplaceTagsParams(NotesParam):
    tag_to_replace: str = Field(..., description="The tag string to be replaced.")
    replace_with_tag: str = Field(..., description="The new tag string to replace with.")

class ReplaceTagsInAllNotesParams(BaseModel):
    tag_to_replace: str = Field(..., description="Tag to replace across all notes.")
    replace_with_tag: str = Field(..., description="New tag to replace with.")

class FindNotesParams(QueryParam):
    pass

class NotesInfoParams(BaseModel):
    notes: Optional[List[int]] = Field(None, description="List of note IDs. Provide 'notes' or 'query'.")
    query: Optional[str] = Field(None, description="Anki search query. Provide 'notes' or 'query'.")

class NotesModTimeParamsNotes(NotesParam):
    pass

class DeleteNotesParams(NotesParam):
    pass

# --- Graphical Action Params ---

class GuiBrowseReorderCardsParams(BaseModel):
    order: Literal["ascending", "descending"] = Field(..., description="Sort order for cards in the browser.")
    columnId: str = Field(..., description="Column identifier to sort by (e.g., 'noteCrt', 'noteMod', 'cardDue').")

class GuiBrowseParams(QueryParam):
    reorderCards: Optional[GuiBrowseReorderCardsParams] = Field(None, description="Optional parameters to reorder cards in the browser.")

class GuiSelectCardParams(CardParam):
    pass

class GuiAddCardsParams(BaseModel):
    note: NoteToAdd = Field(..., description="Note object to pre-fill in the Add Cards dialog.")

class GuiEditNoteParams(NoteIdParam):
    pass

class GuiAnswerCardParams(BaseModel):
    ease: int = Field(..., description="Ease rating for the current card (1-4).")

class GuiDeckOverviewParams(BaseModel):
    name: str = Field(..., description="Name of the deck to open in overview.")

class GuiDeckReviewParams(BaseModel):
    name: str = Field(..., description="Name of the deck to start reviewing.")

class GuiImportFileParams(BaseModel):
    path: str = Field(..., description="Path to the file to import (e.g., .apkg, .txt). Forward slashes on Windows.")

# --- Media Action Params ---

class StoreMediaFileParams(BaseModel):
    filename: str = Field(..., description="Desired filename for the media file within Anki's media collection.")
    data: Optional[str] = Field(None, description="Base64 encoded string of the media file content.")
    path: Optional[str] = Field(None, description="Absolute path to the media file on the local system.")
    url: Optional[str] = Field(None, description="URL to download the media file from.")
    deleteExisting: Optional[bool] = Field(True, description="If true (default), deletes any existing file with the same name before storing the new one.")

class RetrieveMediaFileParams(BaseModel):
    filename: str = Field(..., description="Filename of the media to retrieve.")

class GetMediaFilesNamesParams(BaseModel):
    pattern: str = Field(..., description="Pattern to match media filenames (e.g., '*.jpg', 'sound_*').")

class DeleteMediaFileParams(BaseModel):
    filename: str = Field(..., description="Filename of the media to delete.")

# --- Miscellaneous Action Params ---

class ApiReflectParams(BaseModel):
    scopes: Optional[List[Literal["actions"]]] = Field(None, description="List of scopes to get reflection info for. Currently only 'actions' is supported.")
    actions: Optional[List[str]] = Field(None, description="List of API method names to check. Null for all available actions.")

class LoadProfileParams(BaseModel):
    name: str = Field(..., description="Name of the profile to load.")

class MultiActionItem(BaseModel):
    action: str = Field(..., description="The action to perform for this item.")
    version: Optional[int] = Field(None, description="Optional API version for this specific sub-action.")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for this specific sub-action.")

class MultiParams(BaseModel):
    actions: List[MultiActionItem] = Field(..., description="A list of action objects to perform sequentially.")

class ExportPackageParams(DeckNameParam):
    path: str = Field(..., description="Full path (including filename.apkg) where the package will be saved.")
    includeSched: Optional[bool] = Field(False, description="If true, includes scheduling information in the export.")

class ImportPackageParams(BaseModel):
    path: str = Field(..., description="Path to the .apkg file to import, relative to Anki's collection.media folder.")

# --- Model Action Params ---

class FindModelsByIdParams(BaseModel):
    modelIds: List[int] = Field(..., description="A list of model IDs to find.")

class FindModelsByNameParams(BaseModel):
    modelNames: List[str] = Field(..., description="A list of model names to find.")

class ModelFieldNamesParams(ModelNameParam):
    pass

class ModelFieldDescriptionsParams(ModelNameParam):
    pass

class ModelFieldFontsParams(ModelNameParam):
    pass

class ModelFieldsOnTemplatesParams(ModelNameParam):
    pass

class CardTemplateData(BaseModel):
    Name: Optional[str] = Field(None, description="Name of the card template (e.g., 'Card 1'). Defaults to 'Card N'.")
    Front: str = Field(..., description="HTML/Anki template for the front of the card.")
    Back: str = Field(..., description="HTML/Anki template for the back of the card.")
    bqfmt: Optional[str] = Field(None, description="Optional browser question format.")
    bafmt: Optional[str] = Field(None, description="Optional browser answer format.")

class CreateModelParams(ModelNameParam):
    inOrderFields: List[str] = Field(..., description="List of field names in the desired order for the new model.")
    css: Optional[str] = Field(None, description="CSS styling for the model. Defaults to Anki's built-in CSS if not provided.")
    isCloze: Optional[bool] = Field(False, description="Set to true if this model is a Cloze type.")
    cardTemplates: List[CardTemplateData] = Field(..., description="List of card templates to create for this model.")

class ModelTemplatesParams(ModelNameParam):
    pass

class ModelStylingParams(ModelNameParam):
    pass

class UpdateModelTemplatesModelData(BaseModel):
    name: str = Field(..., description="Name of the model to update.")
    templates: Dict[str, Dict[Literal["Front", "Back"], str]] = Field(..., description="Dictionary mapping card template names to their new Front and Back HTML content.")

class UpdateModelTemplatesParams(BaseModel):
    model: UpdateModelTemplatesModelData = Field(..., description="Model template update data.")

class UpdateModelStylingModelData(BaseModel):
    name: str = Field(..., description="Name of the model whose CSS to update.")
    css: str = Field(..., description="New CSS styling for the model.")

class UpdateModelStylingParams(BaseModel):
    model: UpdateModelStylingModelData = Field(..., description="Model styling update data.")

class FindAndReplaceInModelsModelData(BaseModel):
    modelName: str = Field(..., description="Name of the model to perform find and replace in.")
    findText: str = Field(..., description="The text to find.")
    replaceText: str = Field(..., description="The text to replace with.")
    front: Optional[bool] = Field(True, description="Whether to search in card template fronts.")
    back: Optional[bool] = Field(True, description="Whether to search in card template backs.")
    css: Optional[bool] = Field(True, description="Whether to search in model CSS.")

class FindAndReplaceInModelsParams(BaseModel):
    model: FindAndReplaceInModelsModelData = Field(..., description="Find and replace operation details for a model.")

class ModelTemplateRenameParams(ModelNameParam):
    oldTemplateName: str = Field(..., description="The current name of the template to rename.")
    newTemplateName: str = Field(..., description="The new name for the template.")

class ModelTemplateRepositionParams(ModelNameParam):
    templateName: str = Field(..., description="The name of the template to reposition.")
    index: int = Field(..., description="The new 0-based index for the template.")

class ModelTemplateAddParams(ModelNameParam):
    template: CardTemplateData = Field(..., description="The new card template data to add.")

class ModelTemplateRemoveParams(ModelNameParam):
    templateName: str = Field(..., description="The name of the template to remove.")

class ModelFieldRenameParams(ModelNameParam):
    oldFieldName: str = Field(..., description="The current name of the field to rename.")
    newFieldName: str = Field(..., description="The new name for the field.")

class ModelFieldRepositionParams(ModelNameParam):
    fieldName: str = Field(..., description="The name of the field to reposition.")
    index: int = Field(..., description="The new 0-based index for the field.")

class ModelFieldAddParams(ModelNameParam):
    fieldName: str = Field(..., description="The name of the new field to add.")
    index: Optional[int] = Field(None, description="Optional 0-based index to insert the field at. Defaults to end.")

class ModelFieldRemoveParams(ModelNameParam):
    fieldName: str = Field(..., description="The name of the field to remove.")

class ModelFieldSetFontParams(ModelNameParam):
    fieldName: str = Field(..., description="The name of the field whose font to set.")
    font: str = Field(..., description="The new font name (e.g., 'Arial', 'Courier').")

class ModelFieldSetFontSizeParams(ModelNameParam):
    fieldName: str = Field(..., description="The name of the field whose font size to set.")
    fontSize: int = Field(..., description="The new font size (integer).")

class ModelFieldSetDescriptionParams(ModelNameParam):
    fieldName: str = Field(..., description="The name of the field whose description to set.")
    description: str = Field(..., description="The new description text for the field.")

# --- Statistic Action Params ---
# Actions like getNumCardsReviewedToday, getNumCardsReviewedByDay take no parameters.
# A NoParams model (defined elsewhere or locally in server.py) can be used for them.

class GetCollectionStatsHTMLParams(BaseModel):
    wholeCollection: bool = Field(..., description="True to get stats for the whole collection, false for current deck (if applicable by Anki version).")

class CardReviewsParams(DeckNameParam): 
    # The Anki-Connect doc for 'cardReviews' uses 'deck' which implies deck name.
    startID: int = Field(..., description="Unix timestamp in milliseconds; reviews after this time are returned.")

class GetReviewsOfCardsParams(CardsParam):
    pass

class GetLatestReviewIDParams(DeckNameParam): 
    # The Anki-Connect doc for 'getLatestReviewID' uses 'deck' which implies deck name.
    pass

# For insertReviews, Anki-Connect expects a list of 9-tuples.
# We can model the tuple structure if needed for validation, but the direct type is List[Tuple[...]]
ReviewTuple = Tuple[
    int, # reviewTime (unix ms)
    int, # cardID
    int, # usn (update sequence number, usually -1 for manual entries)
    int, # buttonPressed (ease: 1-4)
    int, # newInterval (in days for reviews, seconds for learning)
    int, # previousInterval
    int, # newFactor
    int, # reviewDuration (ms)
    int  # reviewType (0=learn, 1=review, 2=relearn, 3=cram/filtered)
]

class InsertReviewsParams(BaseModel):
    reviews: List[ReviewTuple] = Field(..., description="List of review entries as 9-tuples: (reviewTime, cardID, usn, buttonPressed, newInterval, previousInterval, newFactor, reviewDuration, reviewType).")

