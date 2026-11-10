<template>
	<div>
		<div class="flex justify-end m-2">
			<Button
				variant="solid"
				:label="'Book'"
				@click="make_appointment_dialog = true"
			>
				<template #prefix>
					<FeatherIcon name="plus" class="h-4" />
				</template>
			</Button>
		</div>
		<div class="py-4 relative min-h-[75vh] flex flex-col">
			<!-- Appointment Grid -->
			<div 
				v-if="paginatedAppointments.length"
				class="flex-1 overflow-y-auto p-2">
				<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
					<Card
						v-for="item in paginatedAppointments"
						:key="item.name"
						class="cursor-pointer rounded-xl border border-gray-200 transition-transform
							hover:scale-105 duration-200 hover:drop-shadow-md p-2 bg-suface-white
							min-h-[170px] min-w-[240px] !shadow-none drop-shadow-xl"
						@click="appointmentDetails(item)"
					>
						<div class="flex items-center justify-between whitespace-nowrap">
							<h3 class="text-xs font-medium text-gray-500 truncate">{{ item.name }}</h3>
							<Badge :variant="'outline'"
								:theme="getStatusColor(item.status)">
								{{ item.status }}
							</Badge>
						</div>

						<p class="mt-2 text-md font-semibold text-gray-800 truncate">
							{{ item.title }}
						</p>

						<p class="mt-1 mb-1 text-xs text-gray-600 leading-snug break-words whitespace-normal">
							<FeatherIcon name="calendar" class="inline w-3 h-3 mr-1 text-gray-500" />
							{{ formatDate(item.appointment_date) }}
						</p>
						<p class="mt-1 text-xs text-gray-600 whitespace-nowrap">
							<FeatherIcon name="clock" class="inline w-3 h-3 mr-1 text-gray-500" />
							{{ item.appointment_time }} ({{ item.duration }} mins)
						</p>
					</Card>
				</div>
			</div>

			<div
				v-else
				class="flex flex-col items-center justify-center flex-grow text-center p-6"
			>
				<FeatherIcon name="file-text" class="w-12 h-12 text-gray-400 mb-3" />
				<h2 class="text-lg font-semibold text-gray-700">No Records Found</h2>
				<p class="text-sm text-gray-500">Looks like you don't have any appointments yet.</p>
			</div>

			<!-- Pagination -->
			<div v-if="paginatedAppointments.length" class="flex justify-center items-center space-x-2 mt-auto pt-2">
				<Button variant="subtle" :disabled="currentPage === 1" @click="currentPage--">
					Prev
				</Button>

				<span class="text-sm text-gray-600">
					Page {{ currentPage }} of {{ totalPages }}
				</span>

				<Button variant="subtle" :disabled="currentPage === totalPages" @click="currentPage++">
					Next
				</Button>
			</div>
		</div>
	</div>

	<BookAppointmentModel
		v-if="make_appointment_dialog"
		v-model="make_appointment_dialog"
		@appointment_booked="get_appointments.reload()"
	/>

	<Dialog v-model="appointment_details" :options="{
		size: '4xl',
	}">
		<template #body-title>
			<div>
				<h2 class="text-xl font-semibold text-gray-900">Appointment Details</h2>
			</div>
			<div class="py-2 flex items-center justify-between gap-2">
				<p class="text-sm text-gray-500"># {{ selectedAppointment.name }}</p>
				<Badge
					:variant="'outline'"
					size="sm"
					:theme="getStatusColor(selectedAppointment.status)">
					{{ selectedAppointment.status }}
				</Badge>
			</div>
		</template>
		<template #body-content>
			<div class="rounded-xl shadow-sm py-2 bg-gray-50">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:[&>section]:h-full">
					<section class="md:col-start-1 md:row-start-1">
						<div class="flex items-start gap-4 px-2">
							<img v-if="selectedAppointment.patient_image" :src="selectedAppointment.patient_image"
								class="w-20 h-20 rounded-full object-cover border" />
							<div v-else
								class="w-20 h-20 rounded-full flex items-center justify-center text-gray-700 text-2xl font-semibold border">
								{{ selectedAppointment.patient_name?.charAt(0)?.toUpperCase() }}
							</div>
							<div>
								<h3 class="text-gray-700 font-medium">Patient</h3>
								<p class="mt-1 text-lg font-semibold text-gray-900">
									{{ selectedAppointment.patient_name }}
								</p>
								<p class="mt-1 text-sm text-gray-600">
									{{ selectedAppointment.patient_email }}
								</p>
							</div>
						</div>
					</section>

					<section class="md:col-start-2 md:row-start-1">
						<div>
							<h3 class="text-gray-700 font-medium">When</h3>
							<p class="mt-1 text-lg font-semibold text-gray-900">
								{{ formatDate(selectedAppointment.appointment_date) }}
							</p>
							<p class="mt-1 text-sm text-gray-600">
								{{ selectedAppointment.appointment_time }} ({{ selectedAppointment.duration }} mins)
							</p>
						</div>
					</section>

					<section class="md:col-start-1 md:row-start-2">
						<div class="flex items-start gap-4 px-2">
							<img v-if="selectedAppointment.practitioner_image"
								:src="selectedAppointment.practitioner_image"
								class="w-20 h-20 rounded-full object-cover border" />
							<div v-else
								class="w-20 h-20 rounded-full flex items-center justify-center text-gray-700 text-2xl font-semibold border">
								{{ selectedAppointment.practitioner_name?.charAt(0)?.toUpperCase() }}
							</div>
							<div>
								<h3 class="text-gray-700 font-medium">Practitioner</h3>
								<p class="mt-1 text-lg font-semibold text-gray-900">
									{{ selectedAppointment.practitioner_name }}
								</p>
								<p class="mt-1 text-sm text-gray-600">
									{{ selectedAppointment.department }}
								</p>
							</div>
						</div>
					</section>

					<section class="md:col-start-2 md:row-start-2">
						<div>
							<div class="flex items-center justify-between">
								<h3 class="text-gray-700 font-medium">Fee</h3>
								<div class="flex items-center justify-between gap-2">
									<Badge :variant="'outline'"
										:theme="selectedAppointment.invoiced == 1 ? 'green' : 'red'">
										{{ selectedAppointment.invoiced ? 'Paid' : 'Unpaid' }}
									</Badge>
									<Button v-if="selectedAppointment.ref_sales_invoice" :ref_for="true" theme="gray" size="md"
										@click="print('Sales Invoice', selectedAppointment.ref_sales_invoice)">
										<Tooltip :text="'Print Invoice'" placement="top">
											<slot name="icon">
												<FeatherIcon :name="'printer'" class="size-4 text-ink-white-7" />
											</slot>
										</Tooltip>
									</Button>
								</div>
							</div>
							<p class="mt-1 text-lg font-semibold text-gray-900">
								{{ formatCurrency(selectedAppointment.paid_amount, selectedAppointment.default_currency) }}
							</p>
							<p v-if="selectedAppointment.ref_sales_invoice" class="mt-1 text-sm text-gray-600">
								# {{ selectedAppointment.ref_sales_invoice }}
							</p>
						</div>
					</section>

					<section v-if="selectedAppointment.encounter" class="md:col-start-1 md:row-start-3">
						<div class="flex items-start gap-4 px-2">
							<div class="w-20"></div>
							<div>
								<h3 class="text-gray-700 font-medium">Prescription ID</h3>
								<div class="flex items-center justify-between gap-10">
									<p class="mt-1 text-lg font-semibold text-gray-900">
										{{ selectedAppointment.encounter }}
									</p>
									<div class="flex items-center gap-2">
										<Button
											v-if="isOwnEncounter(selectedAppointment)"
											variant="solid"
											size="md"
											label="View Visit"
											@click="viewVisit(selectedAppointment.encounter)"
										/>
										<Button :ref_for="true" theme="gray" size="md"
											@click="print('Patient Encounter', selectedAppointment.encounter)">
											<Tooltip :text="'Print Prescription'" placement="top">
												<slot name="icon">
													<FeatherIcon :name="'printer'" class="size-4 text-ink-white-7" />
												</slot>
											</Tooltip>
										</Button>
									</div>
								</div>
							</div>
						</div>
					</section>
				</div>
			</div>
		</template>
	</Dialog>

	<Dialog :options="{
		title: dialog_title,
		message: dialog_message,
		size: 'xl',
		icon: {
			name: 'alert-triangle',
			appearance: 'warning',
		},
		actions: [
			{
				label: 'OK',
				variant: 'solid',
			},
		],
	}" v-model="alert_dialog" @click="alert_dialog = false" />
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import BookAppointmentModel from '@/components/BookAppointmentModel.vue'
import { formatCurrency } from "@/utils/formatters"

import {
	createResource,
	Button,
	Dialog,
	Badge,
	Tooltip
} from 'frappe-ui'

const openVisit = inject('openVisit', null)
const loggedInPatient = inject('loggedInPatient', ref(null))

let appointment_details = ref(false);
let make_appointment_dialog = ref(false);
let alert_dialog = ref(false);

let appointments = ref([]);

const currentPage = ref(1);
const pageSize = 16;

const selectedAppointment = ref("");
let dialog_title = ref("");
let dialog_message = ref("");

let get_appointments = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_appointments",
	method: "GET",
	onSuccess(response) {
		if (response) {
			appointments.value = response;
		}
	},
	onError(error) {
		dialog_message = error.messages?.[0] || error;
		dialog_title = "Failed to load appointments";
		alert_dialog.value = true;
	}
});
get_appointments.fetch();

function appointmentDetails(appointment) {
	selectedAppointment.value = appointment;
	appointment_details.value = true;
}

function isOwnEncounter(appointment) {
	return Boolean(
		appointment?.encounter
		&& loggedInPatient.value?.value
		&& appointment.patient === loggedInPatient.value.value
	)
}

function viewVisit(name) {
	appointment_details.value = false
	if (openVisit) openVisit(name)
}

function print(doctype, docname) {
	const names = Array.isArray(docname) ? docname : [docname]
	const pdfOptions = JSON.stringify({
		"page-size": "A4",
		"margin-top": "60mm",
		"margin-bottom": "60mm",
		"margin-left": "5mm",
		"margin-right": "5mm",
	})
	const w = window.open(
		"/api/method/healthcare.healthcare.api.patient_portal.download_pdf?" +
			"doctype=" + encodeURIComponent(doctype) +
			"&name=" + encodeURIComponent(JSON.stringify(names)) +
			"&options=" + encodeURIComponent(pdfOptions)
	)
	if (!w) {
		alert("Please enable pop-ups")
	}
}

function formatDate(dateStr) {
	return new Date(dateStr).toLocaleDateString("en-IN", {
		weekday: "long",
		year: "numeric",
		month: "long",
		day: "numeric"
	});
}

// Pagination logic
const totalPages = computed(() =>
	Math.ceil(appointments.value.length / pageSize)
);

const paginatedAppointments = computed(() => {
	const start = (currentPage.value - 1) * pageSize;
	return appointments.value.slice(start, start + pageSize);
});

const getStatusColor = (status) => {
	switch (status) {
		case "Confirmed":
			return "green"
		case "Open":
		case "Checked Out":
		case "Scheduled":
			return "orange"
		case "Cancelled":
			return "red"
		case "Checked In":
			return "blue"
		default:
			return "gray"
	}
}
</script>
