#!/usr/bin/env python
###
import docx
import sys, os
import json

###
import click
from docx.enum.style import WD_STYLE_TYPE, WD_STYLE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import RGBColor
from docx.shared import Inches
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

###
from rekdoc import tools

TABLE_RED = "#C00000"
ASSERTION = {1: "Kém", 3: "Cần lưu ý", 5: "Tốt"}


def assert_fault(data):
    if data["fault"] == "No faults found":
        score = 5
        comment = ["Lỗi: Không", "Đánh giá: " + ASSERTION[5]]
    else:
        score = 1
        comment = ["Lỗi ảnh hưởng tới hoạt động của hệ thống", "Đánh giá: " + ASSERTION[1]]

    fault = [score, comment]
    return fault

def assert_temp(data):
    inlet_temp = data["inlet"].split()[0]
    inlet_temp = int(inlet_temp)
    if inlet_temp >= 21 and inlet_temp <= 23:
        score = 5
        comment = ["Nhiệt độ bên trong: " + str(inlet_temp), "Đánh giá: " + ASSERTION[5]]
    elif inlet_temp > 23 and inlet_temp <= 26:
        score = 3
        comment = ["Nhiệt độ bên trong: " + str(inlet_temp), "Đánh giá: " + ASSERTION[5]]
    elif inlet_temp > 26:
        score = 1
        comment = ["Nhiệt độ bên trong: " + str(inlet_temp), "Đánh giá: " + ASSERTION[5]]

    temp = [score, comment]
    return temp 

def assert_firmware(data):
    score = data["firmware"]
    comment = ["Phiên bản Ilom hiện tại: " + data["firmware"], "Phiên bản Ilom mới nhất: "]
    firmware = [score, comment]
    return firmware

def assert_image(data):
    score = data["image"]
    comment = ["Phiên bản OS hiện tại: " + data["image"], "Phiên bản OS mới nhất: "]
    image = [score, comment]
    return image

def assert_vol(data):
    if data["vol_avail"] > 30 and data["raid_stat"] == True:
        score = 5
        comment = [
            "Phân vùng OS được cấu hình RAID",
            "Dung lượng khả dụng: " + str(data["vol_avail"]) + "%",
            "Đánh giá: " + ASSERTION[5],
        ]
    elif (data["vol_avail"] > 15 and data["vol_avail"] <= 30) and data[
        "raid_stat"
    ] == True:
        score = 3
        comment = [
            "Phân vùng OS được cấu hình RAID",
            "Dung lượng khả dụng: " + str(data["vol_avail"]) + "%",
            "Đánh giá: " + ASSERTION[3],
        ]
    elif data["vol_avail"] <= 15 and data["raid_stat"] == False:
        score = 1
        comment = [
            "Phân vùng OS không được cấu hình RAID",
            "Dung lượng khả dụng: " + str(data["vol_avail"]) + "%",
            "Đánh giá: " + ASSERTION[1],
        ]
    elif data["vol_avail"] <= 15 and data["raid_stat"] == True:
        score = 1
        comment = [
            "Phân vùng OS được cấu hình RAID",
            "Dung lượng khả dụng: " + str(data["vol_avail"]) + "%",
            "Đánh giá: " + ASSERTION[1],
        ]

    vol = [score, comment]
    return vol

def assert_bonding(data):
    if data["bonding"] == "none":
        score = 1
        comment = ["Network không được cấu hình bonding"]
    elif data["bonding"] == "aggr":
        score = 5
        comment = ["Network được cấu hình bonding Aggregration"]
    elif data["bonding"] == "ipmp":
        score = 5
        comment = ["Network được cấu hình bonding IPMP"]

    bonding = [score, comment]
    return bonding

def assert_cpu_util(data):
    if data["cpu_util"] <= 30:
        score = 5
    elif data["cpu_util"] > 30 and data["cpu_util"] <= 70:
        score = 3
    else:
        score = 1
    comment = ["CPU Ultilization khoảng " + str(data["cpu_util"]) + "%"]

    cpu_util = [score, comment]
    return cpu_util

def assert_load(data):
    if data["load"]["load_avg_per"] <= 2:
        score = 5
    elif data["load"]["load_avg_per"] > 2 and data["load_avg"]["load_avg_per"] <= 5:
        score = 3
    else:
        score = 1
    comment = [
        "CPU Load Average: " + str(data["load"]["load_avg"]),
        "Number of Cores: " + str(data["load"]["vcpu"]),
        "CPU Load Average per core = CPU Load Average / Number of Cores = "
        + str(data["load"]["load_avg_per"]),
    ]

    load = [score, comment]
    return load

def assert_mem_free(data):
    mem_free = 100 - data["mem_util"]
    if mem_free >= 20:
        score = 5
    elif mem_free > 10 and mem_free < 20:
        score = 3
    else:
        score = 1
    comment = ["Physical memory free: " + str(mem_free) + "%"]

    mem_free = [score, comment]
    return mem_free

def assert_swap_util(data):
    if data["swap_util"] <= 2:
        score = 5
    elif data["swap_util"] > 2 and data["swap_util"] <= 5:
        score = 3
    else:
        score = 1
    comment = ["SWAP Ultilization: " + str(data["swap_util"]) + "%"]

    swap_util = [score, comment]
    return swap_util

def assert_data(data):
    asserted = {}
    for i in data:
        if i == "inlet":
            i = "temp"
        if i == "exhaust":
            continue
        if i == "raid_stat":
            continue
        if i == "mem_util":
            i = "mem_free"
        asserted[i] = ["", []]

    fault = assert_fault(data)
    asserted["fault"][0] = fault[0]
    asserted["fault"][1].extend(fault[1])

    temp = assert_temp(data)
    asserted["temp"][0] = temp[0]
    asserted["temp"][1].extend(temp[1])

    firmware = assert_firmware(data)
    asserted["firmware"][0] = firmware[0]
    asserted["firmware"][1].extend(firmware[1])

    image = assert_image(data)
    asserted["image"][0] = image[0]
    asserted["image"][1].extend(image[1])
    
    vol = assert_vol(data)
    asserted["vol_avail"][0] = vol[0]
    asserted["vol_avail"][1].extend(vol[1])

    bonding = assert_bonding(data)
    asserted["bonding"][0] = bonding[0]
    asserted["bonding"][1].extend(bonding[1])

    cpu_util = assert_cpu_util(data)
    asserted["cpu_util"][0] = cpu_util[0]
    asserted["cpu_util"][1].extend(cpu_util[1])

    load = assert_load(data)
    asserted["load"][0] = load[0]
    asserted["load"][1].extend(load[1])
    
    mem_free = assert_mem_free(data)
    asserted["mem_free"][0] = mem_free[0]
    asserted["mem_free"][1].extend(mem_free[1])


    swap_util = assert_swap_util(data)
    asserted["swap_util"][0] = swap_util[0]
    asserted["swap_util"][1].extend(swap_util[1])

    return asserted


def get_score(asserted):
    checklist = [
        ["STT", "Hạng mục kiểm tra", "Score"],
        [1, "Kiểm tra trạng thái phần cứng", ["", []]],
        [2, "Kiểm tra nhiệt độ", ["", []]],
        [3, "Kiểm tra phiên bản ILOM", ["", []]],
        [4, "Kiểm tra phiên bản Image", ["", []]],
        [5, "Kiểm tra cấu hình RAID và dung lượng phân vùng OS", ["", []]],
        [6, "Kiểm tra cấu hình Bonding Network", ["", []]],
        [7, "Kiểm tra CPU Utilization", ["", []]],
        [8, "Kiểm tra CPU Load Average", ["", []]],
        [9, "Kiểm tra Memory", ["", []]],
        [10, "Kiểm tra Swap", ["", []]],
    ]

    keys = list(asserted)

    for i in range(1, len(checklist)):
        asserted_score = asserted[keys[i-1]][0]
        comment = asserted[keys[i-1]][1]
        try:
            score = ASSERTION[asserted_score]
        except:
            score = asserted_score
        checklist[i][2][0] = score
        checklist[i][2][1] = comment

    return checklist


# #!@#!@#@!
def drw_table(doc, checklist, row, col, info=False):
    if checklist == []:
        return -1
    tab = doc.add_table(row, col)
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab.style = "Table Grid"

    # ADD TITLE CELLS AND COLOR THEM
    cols = tab.rows[0].cells
    for r in range(len(checklist[0])):
        cell = cols[r]
        cell.text = checklist[0][r]
        cell.paragraphs[0].style = "Table Heading"
        shading_elm = parse_xml(
            r'<w:shd {} w:fill="{}"/>'.format(nsdecls("w"), TABLE_RED)
        )
        cell._tc.get_or_add_tcPr().append(shading_elm)

    # ADD CONTENT TO TABLE
    if not info:
        for i in range(1, len(checklist)):
            rows = tab.rows[i]
            cells = rows.cells
            for j in range(0, len(checklist[i])):
                cells[j].text = checklist[i][j]
                cells[j].paragraphs[0].style = "Table Paragraph"
    else:
        for i in range(1, len(checklist)):
            rows = tab.rows[i]
            cells = rows.cells
            for j in range(0, len(checklist[i])):
                if j == (len(checklist[i]) - 1):
                    cells[j].text = checklist[i][j][0]
                    cells[j].paragraphs[0].style = "Table Paragraph"
                    continue
                cells[j].text = str(checklist[i][j])
                cells[j].paragraphs[0].style = "Table Paragraph"
    return tab


def drw_info(doc, node, checklist, images=[]):
    for i in range(1, len(checklist)):
        doc.add_paragraph(checklist[i][1], style="baocao4")
        if isinstance(images[i - 1], list):
            for image in images[i - 1]:
                path = os.path.normpath("output/" + node + "/" + image)
                doc.add_picture(path, width=Inches(6.73))
        else:
            doc.add_picture(
                os.path.normpath("output/" + node + "/" + images[i - 1]),
                width=Inches(6.73),
            )
        for line in checklist[i][2][1]:
            doc.add_paragraph(line, style="Dash List")
    doc.add_page_break()


def define_doc():
    try:
        doc = docx.Document(os.path.normpath("sample/dcx8m2.docx"))
    except Exception as err:
        print("Error:", err)
        sys.exit()
    return doc


def drw_menu(doc, nodes):
    doc.add_paragraph("ORACLE EXADATA X8M-2", style="baocao1")
    doc.add_paragraph("Kiểm tra nhiệt độ môi trường", style="baocao2")
    doc.add_paragraph("Mục lục", style="Heading")
    for node in nodes:
        doc.add_paragraph("Kiểm tra nhiệt độ môi trường", style="baocao2")
        doc.add_paragraph("").paragraph_format.tab_stops.add_tab_stop(
            Inches(1.5), WD_TAB_ALIGNMENT.LEFT, WD_TAB_LEADER.DOTS
        )
    doc.add_page_break()


def drw_doc(doc, input, out_dir, force):
    nodes = tools.read_json(input)
    asserted_list = []
    doc.add_page_break()
    # drw_menu(doc, nodes)
    input_dir = os.path.split(input)[0]
    for node in nodes:
        progress_bar = click.progressbar(
            range(100), label=node, fill_char="*", empty_char=" ", show_eta=False
        )
        image_json = os.path.normpath(input_dir + '/' + node + "/images.json")
        images = tools.read_json(image_json)
        progress_bar.update(10)

        file_dump = {}
        asserted = assert_data(nodes[node])
        progress_bar.update(10)

        file_dump[node] = asserted

        keys = list(asserted)
        checklist = get_score(asserted)
        progress_bar.update(10)
        doc.add_paragraph("Máy chủ " + node, style="baocao2")
        doc.add_paragraph("Thông tin tổng quát", style="baocao3")
        progress_bar.update(10)
        overview = [
            ["Hostname", "Product Name", "Serial Number", "IP Address"],
            [node, "", "", ""],
        ]
        drw_table(doc, overview, 2, 4)
        progress_bar.update(10)
        doc.add_paragraph("Đánh giá", style="baocao3")
        progress_bar.update(10)
        drw_table(doc, checklist, 11, 3, True)
        progress_bar.update(10)

        doc.add_paragraph("Thông tin chi tiết", style="baocao3")
        progress_bar.update(10)

        drw_info(doc, node, checklist, images)
        progress_bar.update(10)

        asserted_file = node + "_asserted"
        asserted_list += [asserted_file]

        tools.save_json(
            os.path.normpath(input_dir + "/" + node + "/" + asserted_file + ".json"),
            file_dump,
        )
        progress_bar.update(10)
        click.secho(" ", nl=False)
        click.secho("DONE", bg="green", fg="black")
        progress_bar.finish()
    file_name = os.path.normpath(tools.rm_ext(input, "json") + "_asserted.json")
    tools.join_json(asserted_list, file_name)
    return doc


def print_style(doc):
    styles = doc.styles
    # p_styles = [s for s in styles if s.type == WD_STYLE_TYPE.PARAGRAPH]
    # p_styles = [s for s in styles if s.type == WD_STYLE_TYPE.TABLE]
    # for style in p_styles:
    for style in styles:
        print(style.name)


def run(input, output, verbose=False, force=False):
    doc = define_doc()
    out_dir = os.path.split(output)[0]
    try:
        doc = drw_doc(doc, input, out_dir, force)
        if doc == -1:
            return -1
    except Exception as err:
        print()
        print(err)
        return -1

    if verbose:
        click.echo()
        click.secho("List of all styles", bg="cyan", fg="black")
        print_style(doc)
        click.echo()
    file_name = os.path.normpath(tools.rm_ext(output, "json") + ".docx")
    doc.save(file_name)
    return file_name


##### MAIN #####
def main():
    run()


if __name__ == "__main__":
    main()
