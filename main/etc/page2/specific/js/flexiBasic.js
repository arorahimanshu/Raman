var flexiselector
var flexibuttonDict = []
var flexicolData = []
var flexiTotal = 0
var flexiNumPages = 10
function setupFlexiGrid(selector, datatype, title, noOfPages, width, height, singleSelect, classData, extraCols,buttonDict,funcDict) {
	/* Structure of buttonDict: [{'name':'button1Name','class':'buttonClass','click':'button1ClickFunc'},{'name':'button2Name','class':'button2Class','click':'button2ClickFunc'}]*/

	
	/*Any key can be omitted in which case default function will be asigned  except bind url
	By default on every event.. request will be send to bind url and after its completion setdata function will be called
	Structure of funcDict:
	{
		'additionalDiv':'selectorForDivInWhichFlexiGridIsContained',
		'bindUrl':urlToSendRequest
		'onPrevPage':prevPageFunc,
		'onNextPage':nextPageFunc,
		'onFirstPage':onFirstPageFunc,
		'onLastPage':onLastPageFunc,
		'onReload':onReloadFunc,
		'onRpChange':onRpChangeFunc,
		'onManualPageEnter':onManualPageEnterFunc,
		'afterInitialize':afterInitializeFunc,
	}
	 */


	flexiselector = selector
	if (datatype == undefined)
		datatype = 'json'
	if (title == undefined)
		title = 'Table'
	if (noOfPages == undefined)
		noOfPages = 10
	if (width == undefined)
		width = 700
	if (height == undefined)
		height = 400
	if (singleSelect == undefined)
		singleSelect = true
	var colData = createColModel(classData)
	if(extraCols != undefined) {
		jQuery.each(extraCols, function (key, value) {

			colData.push(items)
		})
	}
	flexicolData = colData
	var buttons = []
	if(buttonDict != undefined)
	{
		jQuery.each(buttonDict,function(key,buttonItem){
			var button = {}
			button.name = buttonItem.name
			button.onpress = flexiButtonClickFunc
			button.bclass = buttonItem.class
			button.click = buttonItem.click
			buttons.push(button)
			flexibuttonDict.push(button)
		})
	}
	jQuery(selector).flexigrid({
								   dataType: datatype,
								   colModel: colData,
								   usepager: true,
								   buttons: buttons,
								   title: title,
								   useRp: true,
								   rp: noOfPages,
								   showTableToggleBtn: true,
								   width: width,
								   height: height,
								   singleSelect: singleSelect


	})
	
	funcDict.afterinitialize = funcDict.afterInitialize || flexiInitialize
	funcDict.onNextPage = funcDict.onNextPage || onNextPageRequest
	funcDict.onPrevPage = funcDict.onPrevPage || onPrevPageRequest
	funcDict.onFirstPage = funcDict.onFirstPage || onFirstPageRequest
	funcDict.onLastPage = funcDict.onLastPage || onLastPageRequest
	funcDict.onRpChange = funcDict.onRpChange || onRpChange
	funcDict.onReload = funcDict.onReload || onReload
//	funcDict.onManualPageEnter = funcDict.onManualPageEnter || onManualPageEnter

	funcDict.afterinitialize(funcDict.bindUrl)
	jQuery('.pPrev.pButton').click(function () {
		funcDict.onPrevPage(funcDict.bindUrl)
	})
	jQuery('.pNext.pButton').click(function(){
		funcDict.onNextPage(funcDict.bindUrl)
	})
	jQuery('.pGroup select').change(function () {
		funcDict.onRpChange(funcDict.bindUrl)
	})
	jQuery('.pFirst.pButton').click(function () {
		funcDict.onFirstPage(funcDict.bindUrl)
	})
	jQuery('.pLast.pButton').click(function(){
		funcDict.onLastPage(funcDict.bindUrl)
	})
	jQuery('.pReload.pButton').click(function(){
		funcDict.onReload(funcDict.bindUrl)
	})
	jQuery('.pcontrol input').keyup(function (e) {
		var key = e.keyCode || e.which;

		if(key == 13)  // the enter key code
        {
	        if(funcDict.onManualPageEnter != undefined)
			{
				funcDict.onManualPageEnter(funcDict.bindUrl)
			}
	        else
			{
				var pageNo = parseInt(flexiPageValue)
				sendAjaxRequest(funcDict.bindUrl,{'pageNo':pageNo,'rp':flexiNumPages}, setData)

			}
        }
		else
			flexiPageValue = jQuery(this).prop('value')
	});
}

var flexiPageValue = 0
function flexiButtonClickFunc(com, grid){
	var selectedData = []
	var c = 0
	if(jQuery('.trSelected', grid).length > 0) {
		jQuery('.trSelected', grid).each(function () {
			var row = {}
			c += 1
			var rowItem = this
			jQuery.each(flexicolData, function (key, col) {
				row[col.name] = jQuery('td[abbr="' + col.name + '"] >div', rowItem).html()
			})
			selectedData.push(row)
		})
	}
	if(flexibuttonDict != undefined) {
		jQuery.each(flexibuttonDict, function (key, button) {
			if (button.name == com) {
				button['click'](com, grid, c, selectedData)
			}
		})
	}
}

function createColModel(colList) {
	colModel = []
	jQuery.each(colList, function (k, v) {
		var dict = {
			display: v,
			name: v,
			width: v.length * 15,
			align: 'center',
			sortable: true
		}
		colModel.push(dict)
	})
	return colModel

}
function onPrevPageRequest(url)
{
	var pageNo = parseInt(jQuery('.pcontrol input').val()) -1
	sendAjaxRequest(url,{'pageNo':pageNo,'rp':flexiNumPages},setData)
}
function onNextPageRequest(url)
{
	var pageNo = parseInt(jQuery('.pcontrol input').val()) + 1
	sendAjaxRequest(url,{'pageNo':pageNo,'rp':flexiNumPages},setData)
}
function onFirstPageRequest(url)
{
	sendAjaxRequest(url,{'pageNo':1,'rp':flexiNumPages},setData)
}
function onLastPageRequest(url)
{
	var pageNo = parseInt(flexiTotal/10) +1
	sendAjaxRequest(url,{'pageNo':pageNo,'rp':flexiNumPages},setData)
}
function onReload(url)
{
	var pageNo = parseInt(jQuery('.pcontrol input').val())
	sendAjaxRequest(url,{'pageNo':pageNo,'rp':flexiNumPages},setData)
}

function onRpChange(url) {
	var pageNo = parseInt(jQuery('.pcontrol input').val())
	flexiNumPages = parseInt(jQuery('.pGroup select').val())
	sendAjaxRequest(url,{'pageNo':pageNo,'rp':flexiNumPages}, setData)
}
function onManualPageEnter(url) {
	var pageNo = parseInt(jQuery('.pcontrol input').val())
	sendAjaxRequest(url,{'pageNo':pageNo,'rp':flexiNumPages}, setData)
}
function flexiInitialize(url) {
	onFirstPageRequest(url)
}
function setData(data) {
	jQuery(flexiselector).flexAddData(data.message.sendData)
}
